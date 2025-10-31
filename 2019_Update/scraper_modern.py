import requests
from bs4 import BeautifulSoup
import json
import datetime
import os
from time import sleep
import random

def get_movie_data(year):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.imdb.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }
    
    # First visit the homepage
    session = requests.Session()
    try:
        print("Initializing session...")
        session.get('https://www.imdb.com/', headers=headers)
        sleep(2)  # Wait a bit
        
        # Now visit the advanced search page
        print("Visiting search page...")
        session.get('https://www.imdb.com/search/title/', headers=headers)
        sleep(2)  # Wait a bit
        
        # Finally, make the actual search request
        url = f"https://www.imdb.com/search/title/?title_type=feature&release_date={year}&sort=num_votes,desc&count=50"
        print(f"\nFetching movies for year {year}...")
        
        response = session.get(url, headers=headers)
        response.raise_for_status()
        
        # Save the response for debugging
        with open('debug_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        soup = BeautifulSoup(response.text, 'html.parser')
        movies = []
        
        # Find all movie containers - using the new IMDB structure
        movie_containers = soup.find_all('div', class_='ipc-metadata-list-summary-item__tc')
        
        if not movie_containers:
            # Try alternative selectors
            movie_containers = soup.find_all('div', class_='lister-item-content')
            
        if not movie_containers:
            print(f"No movies found for {year}. The page structure might have changed.")
            return None
            
        for i, container in enumerate(movie_containers[:50], 1):
            movie = {}
            
            # Get title - try new IMDB structure first
            title_element = container.find('h3', class_='ipc-title__text')
            if not title_element:
                title_element = container.find('h3', class_='lister-item-header')
                
            if title_element:
                if title_element.a:
                    movie['name'] = title_element.a.text.strip()
                else:
                    movie['name'] = title_element.text.strip()
                if movie['name'].startswith(f"{i}. "):
                    movie['name'] = movie['name'][len(f"{i}. "):]
            
            # Get other metadata
            metadata = container.find_all('span', class_='ipc-metadata-list-item__label')
            for meta in metadata:
                label = meta.text.strip().lower()
                if 'certificate' in label:
                    movie['certificate'] = meta.find_next('span').text.strip()
                elif 'runtime' in label:
                    movie['runtime'] = meta.find_next('span').text.strip()
                elif 'genre' in label:
                    movie['genre'] = meta.find_next('span').text.strip()
            
            # Get description
            desc_element = container.find('div', class_='ipc-html-content-inner-div')
            if desc_element:
                movie['description'] = desc_element.text.strip()
            else:
                # Try old structure
                description = container.find_all('p', class_='text-muted')
                if len(description) > 1:
                    movie['description'] = description[1].text.strip()
                else:
                    movie['description'] = ''
            
            # Get director and stars
            crew_element = container.find('div', class_='ipc-metadata-list-item__content-group')
            if crew_element:
                links = crew_element.find_all('a')
                if links:
                    movie['director'] = links[0].text.strip()
                    movie['stars'] = [link.text.strip() for link in links[1:]]
            else:
                movie['director'] = ''
                movie['stars'] = []
            
            print(f"[{i}/50] Processed: {movie.get('name', 'Unknown Title')}")
            movies.append(movie)
            
            # Random delay between processing movies
            sleep(random.uniform(0.1, 0.3))
            
        return movies
        
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def main():
    # Create DataSets directory if it doesn't exist
    if not os.path.exists('DataSets'):
        os.makedirs('DataSets')
    
    # Just process year 2019 for testing
    year = 2019
    movies = get_movie_data(year)
    
    if movies:
        output_file = os.path.join('DataSets', f'IMDB_Top_50_{year}.json')
        
        # Convert list to dictionary with numbered keys
        movies_dict = {str(i+1): movie for i, movie in enumerate(movies)}
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(movies_dict, f, indent=4, ensure_ascii=False)
        print(f"\nSuccessfully saved data to {output_file}")
    else:
        print("Failed to retrieve movie data")

if __name__ == "__main__":
    main()