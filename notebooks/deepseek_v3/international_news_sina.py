# get the latest financial news from the web

import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import chardet
import json
from datetime import datetime, timedelta
from openai import OpenAI

from keys import DEEPSEEK_API_KEY

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")


def get_latest_international_news():
    # 使用新浪直播API获取国际新闻
    # url = "https://zhibo.sina.com.cn/api/zhibo/feed?page=1&page_size=100&zhibo_id=152&tag_id=102"
    
    try:
        data = []
        for i in range(1, 11):
            print(f"正在获取第 {i} 页") 
            url = f"https://zhibo.sina.com.cn/api/zhibo/feed?page={i}&page_size=100&zhibo_id=152&tag_id=102"
            response = requests.get(url, headers={})
            _current_data = response.json()
            data.extend(_current_data.get('result', {}).get('data', {}).get('feed', {}).get('list', []))
        
        news_list = []
        # 解析新闻条目
        for item in data:
            # 处理新闻内容
            content = item.get('rich_text', '')
            
            # 处理扩展字段
            ext_data = {}
            if 'ext' in item:
                try:
                    ext_data = json.loads(item['ext'])
                except json.JSONDecodeError:
                    ext_data = {}
            
            # 获取新闻链接
            docurl = ext_data.get('docurl', item.get('docurl', ''))
            
            # 获取时间戳并转换为时间对象
            create_time = item.get('create_time', '')
            if create_time:
                try:
                    # 将字符串时间转换为时间对象
                    news_time = datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")
                    # 获取当前时间
                    current_time = datetime.now()
                    # 计算24小时前的时间
                    twenty_four_hours_ago = current_time - timedelta(hours=24)
                    # 只保留24小时内的新闻
                    if news_time < twenty_four_hours_ago:
                        continue
                except ValueError:
                    # 如果时间格式错误，跳过这条新闻
                    continue
            
            # 创建新闻条目
            news_item = {
                'title': content,
                'content': content,
                'url': docurl,
                'timestamp': create_time,
                'tags': [tag['name'] for tag in item.get('tag', [])]
            }
            news_list.append(news_item)
        
        return news_list
    
    except Exception as e:
        print(f"获取国际新闻时出错: {e}")
        return []


def summarize_international_news(news_list):
    """
    使用deepseek-v3模型总结过去24小时的国际新闻要点，返回中英文两个版本
    """
    try:
        if not news_list:
            return {
                'chinese': "过去24小时内没有获取到国际新闻",
                'english': "No international news was retrieved in the past 24 hours"
            }
        
        # 将所有新闻内容合并
        combined_content = "\n".join([f"{item['content']}" for item in news_list])
        
        # 生成中文总结
        prompt = f"请用中文总结以下过去24小时的国际新闻要点，用简洁的bullet points列出最重要的10-20个事件，然后将总结翻译成英文\n\n{combined_content}"
        summary = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content
        
        
        return {
            'summary': summary
        }
    
    except Exception as e:
        print(f"总结国际新闻时出错: {e}")
        return {
            'chinese': "无法生成新闻总结",
            'english': "Failed to generate news summary"
        }


if __name__ == "__main__":
    root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sina_data')
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)

    news_list = get_latest_international_news()
    # Convert news_list to pandas DataFrame
    df = pd.DataFrame(news_list)
    
    # Export to CSV
    df.to_csv(os.path.join(root_dir, 'international_news.csv'), index=False, encoding='utf-8-sig')

    summary = summarize_international_news(news_list)

    # Export summary to JSON file
    with open(os.path.join(root_dir, 'international_news_summary.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=4)

    # 将摘要写入txt文件
    with open(os.path.join(root_dir, 'international_news_summary.md'), 'w+', encoding='utf-8') as f:
        print(summary['summary'], file=f)
