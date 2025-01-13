# get the latest financial news from the web

import requests
from bs4 import BeautifulSoup
import time
import chardet

def get_latest_financial_news():
    url = "https://finance.sina.com.cn/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    
    max_retries = 3
    retry_delay = 2  # seconds
    timeout = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            # Detect encoding automatically
            detected_encoding = chardet.detect(response.content)['encoding']
            response.encoding = detected_encoding if detected_encoding else 'gbk'
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            # print(soup.prettify())
            
            # Updated selector to match current Sina Finance structure
            news_items = soup.find_all('div', class_='m-p1-rb3-content')
            if news_items:
                headlines = []
                for item in news_items:
                    links = item.find_all('a')
                    for link in links:
                        if link.text.strip():
                            headlines.append(link.text.strip())
                if headlines:
                    return f"最新财经新闻: {'; '.join(headlines[:3])}"  # Return top 3 headlines
            return "未找到新闻标题"
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return f"获取新闻失败: {str(e)}"

if __name__ == "__main__":
    print(get_latest_financial_news())
