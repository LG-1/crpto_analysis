from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import sys

from utils import init_driver

def get_ele_text(elem, selector):
    """获取元素文本"""
    try:
        return elem.select_one(selector).get_text(strip=True)
    except Exception as e:
        print(f"获取元素文本时出错: {str(e)}", file=sys.stderr)
        return "无"
    

def scrape_all_pages(driver, base_url):
    jobs = []
    page_num = 1
    try:
        while True:
            # 访问页面
            url = f"{base_url}&currentPage={page_num}"
            driver.get(url)
            
            # 等待页面加载完成
            time.sleep(5)  # 基础等待
            
            # 显式等待职位列表加载
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.list-card-item1'))
                )
            except:
                print("等待职位列表超时，尝试继续解析", file=sys.stderr)
            
            # 获取完整页面源码
            page_source = driver.page_source
            
            # 使用BeautifulSoup解析
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # # 调试：保存完整页面
            # with open('dynamic_page.html', 'w', encoding='utf-8') as f:
            #     f.write(soup.prettify())
            
            # 尝试多种选择器组合
            job_list = []
            
            # 尝试1: 查找包含职位信息的卡片
            job_cards = soup.select('.list-card-item1')
            
            if not job_cards:
                # 尝试2: 查找所有可能包含职位信息的div
                job_divs = soup.find_all('div', class_=lambda x: x and ('job' in x or 'position' in x or 'recruit' in x))
                job_cards = job_divs
            
            for card in job_cards:
                try:
                    job = {}
                    job['PostId'] = card.get('id', '无')
                    job['职位名称'] = get_ele_text(card, '.top-label')
                    job['职位类别'] = get_ele_text(card, '.pos-tag-item')
                    job['雇佣类别'] = get_ele_text(card, '.work-type')
                    job['工作地点'] = get_ele_text(card, '.location, .city, .area, .work-place')
                    job['发布时间'] = get_ele_text(card, '.time, .publish-time, .date, .pub-time')

                    job_list.append(job)
                except Exception as e:
                    print(f"解析单个职位时出错: {str(e)}", file=sys.stderr)
                    continue

            jobs.extend(job_list)

            page_control = soup.select_one('.ant-pagination-next').get('aria-disabled', 'false')
            if page_control == 'true':
                print(f"共解析了{page_num}页数据, 没有更多页面可供解析")
                break
            
            page_num += 1

    except Exception as e:
        print(f"发生错误: {str(e)}", file=sys.stderr)
        __result__ = {
            "status": "error",
            "message": str(e),
            "traceback": str(sys.exc_info())
        }
    
    return jobs


def get_job_info(driver, job):
    """获取单个职位的详细信息"""
    job_id = job["PostId"]
    detail_url = "https://career.yonyou.com/SU67ac41886202cc7916ae3029/pb/posDetail.html?postId={job_id}&postType=society"
    driver.get(detail_url.format(job_id=job_id))
    
    # 等待页面加载完成
    time.sleep(1)  # 基础等待
    # 获取完整页面源码
    page_source = driver.page_source
    
    # 使用BeautifulSoup解析
    soup = BeautifulSoup(page_source, 'html.parser')
    detail_cards = soup.select(".post-detail__module")

    job['工作职责'] = get_ele_text(detail_cards[0], '.detail')
    job['岗位要求'] = get_ele_text(detail_cards[1], '.detail')

    return job


if __name__ == "__main__":
    # 初始化浏览器
    driver = init_driver()
    index_url = "https://career.yonyou.com/SU67ac41886202cc7916ae3029/pb/social.html?workPlaceCode=0%2F4%2F10"  # 上海职位过滤条件
    # 保存到JSON文件
    jobs_list = scrape_all_pages(driver, index_url)

    all_jobs = []
    for ind, job in enumerate(jobs_list):
        print(f"正在获取第{ind + 1}个职位的详细信息: {job['职位名称']}")
        # 获取单个职位的详细信息
        job = get_job_info(driver, job)
        all_jobs.append(job)

    file_pth = 'yonyou/yonyou_sh_jobs.json'
    with open(file_pth, 'w', encoding='utf-8') as f:
        json.dump(all_jobs, f, ensure_ascii=False, indent=2)

    driver.quit()
    