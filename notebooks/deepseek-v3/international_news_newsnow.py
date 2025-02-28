# I want to get the latest international news list from https://www.newsnow.com/ca/World?type=ln

import requests
from bs4 import BeautifulSoup

url = "https://www.newsnow.com/ca/World?type=ln"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Extract headlines and timestamps
articles = soup.find_all('div', class_='hl')


news_list = []
for article in articles:
    headline = article.find('a', class_='hll')
    timestamp = article.find('span', class_='time')
    
    if headline and timestamp:
        news_list.append({
            'headline': headline.text.strip(),
            'timestamp': timestamp.text.strip(),
            'link': headline['href']
        })

# Print or process the news list
for news in news_list:
    print(f"{news['timestamp']} - {news['headline']}")






