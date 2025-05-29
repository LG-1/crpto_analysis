import requests
import time
import json
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import urljoin
import os, sys
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import numpy as np
import pandas as pd

from utils import init_driver, save_to_json, read_json, expand_single_job_info

# 全局配置
REQUEST_DELAY = 2  # 请求间隔(秒)
MAX_RETRIES = 3    # 最大重试次数

        
def switch_to_sh(driver, url, retry=0):
    driver.get(url)
    wait_time = 1
    
    # 上海
    city_trigger = WebDriverWait(driver, wait_time).until(EC.element_to_be_clickable((By.CLASS_NAME, "option-item-select-city")))
    city_trigger.click()
    
    # 根据 input 属性定位选项
    shanghai_option = WebDriverWait(driver, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//div[@title='上海']")))
    shanghai_option.click()

    # IT互联网技术
    cate_trigger = WebDriverWait(driver, wait_time).until(EC.element_to_be_clickable((By.CLASS_NAME, "option-item-select-job")))
    cate_trigger.click()
    # time.sleep(2)

    # 根据 input 属性定位选项
    it_option = WebDriverWait(driver, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//div[@title='IT互联网技术']")))
    it_option.click()
    time.sleep(2)

def parse_job_list(html):
    soup = BeautifulSoup(html, 'html.parser')
    jobs = []
    
    job_items = soup.select('div.job-detail-box')  # div.job-list-item 

    
    for item in job_items:
        try:
            job = {
                'title': item.select_one('div.ellipsis-1').get_text(),
                'url': item.select_one('a')['href'],
                'salary': item.select_one('span.job-salary').get_text(strip=True),
                'location': item.select_one('span.ellipsis-1').get_text(strip=True),
                'education': item.select_one('span.labels-tag').get_text(strip=True)
            }
            
            jobs.append(job)
        except Exception as e:
            print(e)
    
    return jobs

def scrape_all_jobs(driver, base_url=''): 
    def expand_jobs_info(jobs):
        all_jobs = []
        for job in jobs:
            job = expand_single_job_info(job)
            print(f"已抓取: {job['title']}")
            all_jobs.append(job)

        return all_jobs


    def is_last_page(driver):
        try:
            # 定位下一页按钮的父级 <li>
            next_btn_li = driver.find_element(By.CLASS_NAME, "ant-pagination-next")
            
            # 同时检查类名和 aria 属性
            is_disabled_class = "ant-pagination-disabled" in next_btn_li.get_attribute("class")
            is_aria_disabled = next_btn_li.get_attribute("aria-disabled") == "true"
            
            return is_disabled_class or is_aria_disabled
        except:
            return True
    
    all_jobs = []
    page = 1

    switch_to_sh(driver, f"{base_url}")
    html = driver.page_source
    
    while True:      
        print(f"正在处理第 {page} 页")  
        if not html:
            break

        jobs = parse_job_list(html)
        if not jobs:
            break
            
        all_jobs.extend(jobs)

        if is_last_page(driver):
            print(f"共解析了{page}页数据, 共{len(all_jobs)}个职位, 没有更多页面可供解析")
            break

        next_trigger = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CLASS_NAME, "ant-pagination-next")))
        next_trigger.click()
        time.sleep(REQUEST_DELAY)
        html = driver.page_source

        page += 1

    all_jobs = expand_jobs_info(all_jobs)
    return all_jobs



def main(base_url='', output_file=''):
    driver = init_driver()
    try:
        jobs = scrape_all_jobs(driver, base_url)
        if jobs:
            save_to_json(jobs, output_file)
            __result__ = {
                "status": "success",
                "count": len(jobs),
                "file": os.path.abspath(output_file)
            }
        else:
            __result__ = {
                "status": "warning",
                "message": "未抓取到任何职位数据"
            }
    except Exception as e:
        print(f"发生错误: {e}", file=sys.stderr)
        __result__ = {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    sub_folder = "liepin-20250528"

    root_path = os.path.dirname(os.path.abspath(__file__))
    root_folder = os.path.join(root_path, sub_folder)
    if not os.path.exists(root_folder):
        os.makedirs(root_folder)

    company_map = {"申通快递": "8076592", "用友": "5634845"}
    debug_companies = ["SHEIN"]

    meta_df = pd.read_excel("input/meta_df/备选公司列表.xlsx")
    meta_df['liepin_id'] = meta_df['liepin_id'].fillna('').map(lambda x: str(int(x)) if x else '')
    company_map = {k: v for k, v in zip(meta_df['公司名称'], meta_df['liepin_id']) if v 
                #    and k in debug_companies
                   }
    print(company_map)

    for company_name, company_id in company_map.items():
        base_url = f"https://www.liepin.com/company-jobs/{company_id}/"
        output_file_name = f"liepin_jobs_{company_name}.json"

        if output_file_name in os.listdir(root_folder):
            print(f"文件 {output_file_name} 已存在，跳过抓取")
            continue

        print(f"\n\n===================正在抓取 {company_name} 的职位数据...")
        output_file = f"{sub_folder}/{output_file_name}"
        main(base_url, output_file)
        # time.sleep(15)
