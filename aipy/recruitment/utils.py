import requests
import time
import json
from bs4 import BeautifulSoup
import os, sys

from fake_useragent import UserAgent

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


root_path = os.path.dirname(os.path.abspath(__file__))
DRIVER_PTH = os.path.join(root_path, "chromedriver")


def get_random_headers():
    ua = UserAgent()
    return {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.liepin.com/'
    }

def init_driver():
    """https://googlechromelabs.github.io/chrome-for-testing/#stable"""
    """初始化Selenium WebDriver"""
    ua = UserAgent(browsers=['chrome'], os=['Mac'], platforms=['desktop'])
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={ua.random}")
    
    try:
        # driver = webdriver.Chrome(options=options)
        # driver.set_page_load_timeout(CONFIG["timeout"])

        service = Service(executable_path=DRIVER_PTH)
        driver = webdriver.Chrome(service=service, options=options)

        return driver
    except Exception as e:
        print(f"Error initializing WebDriver: {str(e)}", file=sys.stderr)
        return None
    

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存到 {filename}")

def read_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def expand_single_job_info(job):
    # 使用requests获取页面源码
    headers = {'User-Agent': UserAgent().random}
    response = requests.get(job['url'], headers=headers)
    response.raise_for_status()  # 检查请求是否成功
    
    # 解析HTML内容
    detail_soup = BeautifulSoup(response.text, 'html.parser')
    print(detail_soup)

    company_card = detail_soup.select_one('.company-card')
    company_name = company_card.select_one(".ellipsis-1").get_text(strip=True)
    company_url = company_card['data-href']

    paragraphs = detail_soup.select_one('.job-intro-container').select('.paragraph')

    if len(paragraphs) > 0:
        job['职位介绍'] = paragraphs[0].select_one('dd').get_text(strip=True)

    if len(paragraphs) > 1:
        job['其它信息'] = paragraphs[1].select_one('dd').get_text(strip=True)

    job['公司名称'] = company_name
    job['公司链接'] = company_url

    return job