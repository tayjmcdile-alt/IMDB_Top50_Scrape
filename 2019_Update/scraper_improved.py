import requests
from bs4 import BeautifulSoup
import json
import datetime
import pprint
import sys
import os

pp = pprint.PrettyPrinter(indent=4)

def main():  # Main function
    # Create DataSets directory if it doesn't exist
    if not os.path.exists('DataSets'):
        os.makedirs('DataSets')

    current_year = int(datetime.datetime.now().year)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Just doing one year for testing
    year = 2019
    print(f"Scraping data for year {year}...")
    
    output_file = os.path.join('DataSets', f'IMDB_Top_50_{year}.json')
    url = f"https://www.imdb.com/search/title?release_date={year},{year}&title_type=feature"
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch data: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, features="html.parser")
    dataset_top50 = {}
    id = 1
    movies_list = soup.findAll('div', attrs={'class': 'lister-item-content'})
    
    for each in movies_list:
        # Prototype of each movie item
        movie_item = {
            'name': '',
            'certificate': '',
            'runtime': '',
            'genre': '',
            'description': '',
            'director': '',
            'stars': []
        }

        if each.find('h3', attrs={'class': 'lister-item-header'}).find('a'):
            name_value = each.find('h3', attrs={'class': 'lister-item-header'}).find('a').text.strip()
            movie_item['name'] = name_value

        p_list = each.findAll('p')

        if p_list and len(p_list) > 0:
            if p_list[0].find('span', attrs={'class': 'certificate'}):
                certificate_value = p_list[0].find('span', attrs={'class': 'certificate'}).text.strip()
                movie_item['certificate'] = certificate_value

            if p_list[0].find('span', attrs={'class': 'runtime'}):
                runtime_value = p_list[0].find('span', attrs={'class': 'runtime'}).text.strip()
                movie_item['runtime'] = runtime_value

            if p_list[0].find('span', attrs={'class': 'genre'}):
                genre_value = p_list[0].find('span', attrs={'class': 'genre'}).text.strip()
                movie_item['genre'] = genre_value

        if len(p_list) > 1:
            description_value = p_list[1].text.strip()
            movie_item['description'] = description_value

        dataset_top50[id] = movie_item
        id += 1
        print(f"Processed movie: {movie_item['name']}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset_top50, f, indent=4, ensure_ascii=False)
    
    print(f"\nData saved to {output_file}")

if __name__ == "__main__":
    main()