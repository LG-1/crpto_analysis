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

import requests
import time
import json


def get_company_jobs(comp_id):
    url = 'https://api-c.liepin.com/api/com.liepin.searchfront4c.pc-comp-homepage-search-job'
    start_page = {"location": f"https://www.liepin.com/company-jobs/{comp_id}/"}

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://www.liepin.com',
        'Pragma': 'no-cache',
        'Referer': 'https://www.liepin.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': UserAgent().random,
        # 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'X-Client-Type': 'web',
        'X-Fscp-Bi-Stat': json.dumps(start_page),
        'X-Fscp-Fe-Version': '', 
        'X-Fscp-Std-Info': '{"client_id": "40108"}',
        'X-Fscp-Trace-Id': '32719e6c-e80d-45dd-9754-3fdc3b8576c7',
        'X-Fscp-Version': '1.1',
        'X-Requested-With': 'XMLHttpRequest',
        'X-XSRF-TOKEN': '9kwtlMkGTTGkerYyxwWwQw',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'Cookie': 'inited_user=6614e17a135bf2595bed49c2a8bf029e; XSRF-TOKEN=9kwtlMkGTTGkerYyxwWwQw; __gc_id=d0303eb7425e4032af3fafc4ced7b97d; __uuid=1747884095753.37; __tlog=1747884095759.30%7C00000000%7C00000000%7Cs_o_009%7Cs_o_009; Hm_lvt_a2647413544f5a04f00da7eee0d5e200=1747884096; HMACCOUNT=FE574B62D658107B; _ga=GA1.1.659964502.1747884097; hpo_role-sec_project=sec_project_liepin; hpo_sec_tenant=0; user_roles=0; user_photo=5f8fa3a78dbe6273dcf85e2608u.png; user_name=%E6%9D%8E%E5%85%88%E7%94%9F; need_bind_tel=false; new_user=false; c_flag=b12a610049656730ac34cebb146fb8f3; inited_user=6614e17a135bf2595bed49c2a8bf029e; imId=523337c5a9661e714f2a5f6d3324f90e; imId_0=523337c5a9661e714f2a5f6d3324f90e; imClientId=523337c5a9661e71f158ed17979abd7f; imClientId_0=523337c5a9661e71f158ed17979abd7f; imApp_0=1; fe_im_connectJson_0=%7B%220_82ccfe162f0560e341344312b1f2ca2b%22%3A%7B%22socketConnect%22%3A%222%22%2C%22connectDomain%22%3A%22liepin.com%22%7D%7D; fe_im_socketSequence_new_0=50_47_46; fe_im_opened_pages=; _ga_54YTJKWN86=GS2.1.s1748486975$o13$g1$t1748488710$j60$l0$h0; acw_tc=2760829017484887111558752e78e1fa6263b6099bfef8b3e1e2423fa500ea; Hm_lpvt_a2647413544f5a04f00da7eee0d5e200=1748488720; __session_seq=866; __tlg_event_seq=3648'
    }

    # 基础请求数据
    base_data = {
        "data": {
            "compJobSearchCondition": {
                "compId": comp_id,
                "dq": "020", # 地区代码，020代表上海
                "jobTitleCode": "N02", # 职位代码，N02代表IT互联网技术
                "pageSize": 30,  # 每页数量保持不变
                "curPage": 0     # 当前页会动态修改
            },
            "passThroughForm": {
                "ckId": "e8fl2gm3j0ldliddmzn78x2yu4nl4cz8",
                "skId": "m19o22x3aijga9el7nqjf0brfe1fm3c8",
                "fkId": "sh8iv9nizxd1be0wcbie5q5eow97vc2a",
                "scene": "condition",
                "sfrom": "search_job_comp_prime_pc"
            }
        }
    }

    # 存储所有结果
    all_results = []

    try:
        # 先获取第一页数据以确定总页数
        response = requests.post(url, headers=headers, json=base_data)
        response.raise_for_status()  # 检查HTTP错误
        
        first_page_data = response.json()
        all_results.append(first_page_data)
        # print(all_results)
        
        # 解析分页信息
        pagination = first_page_data.get('data', {}).get('pagination', {})
        total_pages = pagination.get('totalPage', 1)
        
        print(f"总页数: {total_pages}, 总记录数: {pagination.get('totalCounts', 0)}")
        
        # 从第二页开始获取剩余页数据（页数从0开始）
        for page in range(1, total_pages):
            # 更新当前页码
            base_data['data']['compJobSearchCondition']['curPage'] = page
            
            # 发送请求
            response = requests.post(url, headers=headers, json=base_data)
            response.raise_for_status()
            
            page_data = response.json()
            all_results.append(page_data)
            
            # 显示进度
            print(f"已获取第 {page + 1}/{total_pages} 页数据")
            
            # 添加适当延迟避免请求过快
            time.sleep(0.2)
        
        print(f"\n成功获取所有 {total_pages} 页数据！")
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

    # 如果需要，可以在这里处理合并后的数据
    # 例如：提取所有职位信息
    all_jobs = []
    for result in all_results:
        jobs = result.get('data', {}).get('data', [])
        all_jobs.extend(jobs)

    print(f"总共获取了 {len(all_jobs)} 个职位信息")

    return all_jobs

if __name__ == "__main__":
    sub_folder = "liepin-api-20250528"
    raw = "raw"

    root_path = os.path.dirname(os.path.abspath(__file__))
    root_folder = os.path.join(root_path, sub_folder, raw)
    if not os.path.exists(root_folder):
        os.makedirs(root_folder)

    # get_company_jobs(8076592) 
    company_map = {"申通快递": "8076592", "用友": "5634845"}
    debug_companies = ["SHEIN"]

    meta_df = pd.read_excel("input/meta_df/备选公司列表.xlsx")
    meta_df['liepin_id'] = meta_df['liepin_id'].fillna('').map(lambda x: str(int(x)) if x else '')
    company_map = {k: v for k, v in zip(meta_df['公司名称'], meta_df['liepin_id']) if v 
                   and k in debug_companies
                   }
    print(company_map)

    total_jobs_cnt = 0
    for company_name, company_id in company_map.items():
        output_file_name = f"liepin_jobs_{company_name}.json"

        if output_file_name in os.listdir(root_folder):
            print(f"文件 {output_file_name} 已存在，跳过抓取")
            continue

        print(f"\n\n===================正在抓取 {company_name} 的职位数据...")
        output_file = os.path.join(root_path, sub_folder, raw, output_file_name)
        comp_jobs = get_company_jobs(company_id)
        total_jobs_cnt += len(comp_jobs)

        flattened_jobs = []
        for job in comp_jobs:
            job = {**job['job'], **job['recruiter'], "company_id": company_id, "company_name": company_name}
            job['url'] = job.pop("link")
            flattened_jobs.append(job)
        save_to_json(flattened_jobs, output_file)

    handled_cnt = 0
    for file_name in os.listdir(os.path.join(root_path, sub_folder, raw)):
        if file_name.endswith('.json'):
            file_path = os.path.join(root_path, sub_folder, raw, file_name)
            cur_comp_jobs = read_json(file_path)

            extended_jobs = []
            for job in cur_comp_jobs:
                print(f"{handled_cnt+1}/{total_jobs_cnt} 正在扩展职位信息: {job['company_name']} -> {job['title']}")
                job = expand_single_job_info(job)
                extended_jobs.append(job)
                handled_cnt += 1
            save_to_json(extended_jobs, os.path.join(root_path, sub_folder, file_name))

