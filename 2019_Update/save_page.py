import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

url = "https://www.imdb.com/search/title?release_date=2019,2019&title_type=feature"
response = requests.get(url, headers=headers)

with open('page_content.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("Page content saved to page_content.html")