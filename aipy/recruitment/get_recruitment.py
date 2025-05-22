import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin
import logging

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('recruitment.log'), logging.StreamHandler()]
)

COMPANY_CONFIGS = {
    "腾讯": {
        "type": "api",
        "url": "https://careers.tencent.com/tencentcareer/api/post/Query",
        "params": {"pageIndex": 1, "pageSize": 100, "language": "zh-cn"},
        "pagination": True,  # 新增分页支持
        "parser": lambda data: [
            {
                "title": item.get("RecruitPostName", "未提供职位名称"),
                "link": f"https://careers.tencent.com/position/detail/{item.get('PostId', '')}",
                "location": item.get("LocationName", "未明确地点"),
                "category": item.get("CategoryName", "未分类")
            }
            for item in data.get("Data", {}).get("Posts", [])
        ]
    },
    "美团": {
        "type": "hybrid",
        "main_url": "https://zhaopin.meituan.com/social",
        "backup_url": "https://zhaopin.meituan.com/api/job/list?jobType=social",
        "selectors": {
            "container": ".job-list-wrapper",
            "item": ".job-item",
            "title": ".job-name",
            "link": "a",
            "department": ".department"
        }
    }
}

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15'
]

PROXIES = {
    'http': 'http://10.10.1.10:3128',
    'https': 'http://10.10.1.10:1080'
}

TIMEOUT = 20
RETRIES = 3

def enhanced_request(url, method='GET', params=None, headers=None):
    """增强型请求函数，支持轮换User-Agent和代理"""
    headers = headers or {'User-Agent': random.choice(USER_AGENTS)}
    attempt = 0
    
    while attempt < RETRIES:
        try:
            response = requests.request(
                method,
                url,
                params=params,
                headers=headers,
                timeout=TIMEOUT,
                proxies=PROXIES if random.random() < 0.3 else None  # 30%概率使用代理
            )
            response.raise_for_status()
            
            if response.status_code == 200 and response.text.strip():
                return response
                
        except requests.exceptions.RequestException as e:
            logging.warning(f"Attempt {attempt+1} failed: {str(e)}")
            if attempt == RETRIES - 1:
                logging.error(f"最终请求失败: {url}")
                return None
                
        time.sleep(random.uniform(2, 5))
        attempt += 1

def handle_pagination(config):
    """处理分页逻辑"""
    all_data = []
    page = 1
    while True:
        params = config["params"].copy()
        params["pageIndex"] = page
        response = enhanced_request(config["url"], params=params)
        
        if not response:
            break
            
        try:
            data = response.json()
            current_data = config["parser"](data)
            if not current_data:
                break
            all_data.extend(current_data)
            
            # 腾讯的TotalCount逻辑
            if page * params["pageSize"] >= data.get("Data", {}).get("TotalCount", 0):
                break
                
            page += 1
            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            logging.error(f"分页处理异常: {str(e)}")
            break
            
    return all_data

def parse_meituan():
    """美团混合解析器"""
    config = COMPANY_CONFIGS["美团"]
    positions = []
    
    # 尝试主站解析
    response = enhanced_request(config["main_url"])
    if response and response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        container = soup.select_one(config["selectors"]["container"])
        
        if container:
            for item in container.select(config["selectors"]["item"]):
                try:
                    positions.append({
                        "title": item.select_one(config["selectors"]["title"]).text.strip(),
                        "link": urljoin(config["main_url"], item.select_one(config["selectors"]["link"])["href"]),
                        "department": item.select_one(config["selectors"]["department"]).text.strip() 
                            if item.select_one(config["selectors"]["department"]) else "未指定部门"
                    })
                except AttributeError as e:
                    logging.warning(f"元素解析失败: {str(e)}")
                    continue
                    
    # 备用API方案                
    if not positions:
        response = enhanced_request(config["backup_url"])
        if response and response.status_code == 200:
            try:
                data = response.json()
                positions = [{
                    "title": item.get("jobName", "未命名职位"),
                    "link": urljoin(config["main_url"], f"/job/{item.get('jobId', '')}"),
                    "department": item.get("department", "未指定部门")
                } for item in data.get("data", [])]
            except ValueError:
                logging.error("美团备用API JSON解析失败")
                
    return positions

def main():
    all_positions = []
    
    for company, config in COMPANY_CONFIGS.items():
        logging.info(f"开始采集 {company} 数据")
        positions = []
        
        try:
            if config["type"] == "api":
                if config.get("pagination"):
                    positions = handle_pagination(config)
                else:
                    response = enhanced_request(config["url"], params=config.get("params"))
                    positions = config["parser"](response.json()) if response else []
                    
            elif config["type"] == "hybrid" and company == "美团":
                positions = parse_meituan()
                
            if positions:
                logging.info(f"{company} 获取到 {len(positions)} 个职位")
                all_positions.extend([{"company": company, **p} for p in positions])
                # 数据去重
                df_temp = pd.DataFrame(all_positions)
                df_temp = df_temp.drop_duplicates(subset=["company", "link"])
                all_positions = df_temp.to_dict("records")
                
        except Exception as e:
            logging.error(f"{company} 采集失败: {str(e)}")
            continue
            
        time.sleep(random.randint(2, 6))
        
    if all_positions:
        df = pd.DataFrame(all_positions)
        with pd.ExcelWriter('recruitment_data.xlsx', engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
            # 自动调整列宽
            worksheet = writer.sheets['Sheet1']
            for idx, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(idx, idx, max_len)
                
        logging.info(f"成功保存 {len(df)} 条数据")
    else:
        logging.warning("未获取到有效数据")

if __name__ == '__main__':
    main()