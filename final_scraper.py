import requests
from bs4 import BeautifulSoup
import json
import os
from time import sleep

def get_movies(year):
    # Updated headers to look more like a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'DNT': '1'
    }
    
    # First visit IMDB homepage
    session = requests.Session()
    print("Initializing session...")
    session.get('https://www.imdb.com/', headers=headers)
    sleep(2)  # Wait a bit
    
    # Then visit the search page
    print("Navigating to search...")
    session.get('https://www.imdb.com/search/title/', headers=headers)
    sleep(2)  # Wait a bit
    
    # Finally make the actual search request
    url = f"https://www.imdb.com/search/title/?title_type=feature&release_date={year}&sort=num_votes,desc&count=50"
    print(f"\nFetching movies for {year}...")
    
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save the HTML for debugging
        with open('debug.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        # Try both old and new IMDB layouts
        movie_containers = soup.find_all('div', class_='lister-item-content')
        if not movie_containers:
            movie_containers = soup.find_all('div', class_='ipc-metadata-list-summary-item__tc')
            
        if not movie_containers:
            print("No movies found. IMDB might be blocking our request.")
            print("Try again in a few minutes or use a different year.")
            return False
            
        print(f"\nTop Movies from {year}:")
        print("-" * 50)
        
        movies = []
        for i, container in enumerate(movie_containers, 1):
            movie = {}
            
            # Try to get title (multiple possible layouts)
            title_element = container.find('h3', class_='lister-item-header')
            if title_element and title_element.find('a'):
                title = title_element.find('a').text.strip()
            else:
                title_element = container.find('h3', class_='ipc-title__text')
                if title_element:
                    title = title_element.text.strip()
                    if title.startswith(f"{i}. "):
                        title = title[len(f"{i}. "):]
                else:
                    continue
                    
            movie['title'] = title
                
            # Get rating
            rating_element = container.find('div', class_='ratings-imdb-rating')
            if rating_element:
                rating = rating_element.get('data-value', 'N/A')
            else:
                rating_element = container.find('span', class_='ipc-rating-star')
                rating = rating_element.text.strip() if rating_element else 'N/A'
            movie['rating'] = rating
            
            # Get description
            desc_element = container.find('div', class_='ipc-html-content-inner-div')
            if desc_element:
                plot = desc_element.text.strip()
            else:
                description = container.find_all('p', class_='text-muted')
                if len(description) > 1:
                    plot = description[1].text.strip()
                else:
                    plot = "No description available"
            movie['plot'] = plot
            
            print(f"\n{i}. {title}")
            print(f"   Rating: {rating}")
            print(f"   Plot: {plot[:150]}...")  # Show first 150 characters of plot
            
            movies.append(movie)
            sleep(0.1)  # Small delay between processing movies
        
        # Save to file
        if not os.path.exists('DataSets'):
            os.makedirs('DataSets')
            
        output_file = os.path.join('DataSets', f'IMDB_Top_50_{year}.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(movies, f, indent=4, ensure_ascii=False)
            
        print(f"\nSaved {len(movies)} movies to {output_file}")
        return True
        
    except requests.RequestException as e:
        print(f"Error accessing IMDB: {str(e)}")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False

def main():
    year = input("Enter the year to fetch movies from (e.g., 2019): ")
    try:
        year = int(year)
        get_movies(year)
    except ValueError:
        print("Please enter a valid year!")

if __name__ == "__main__":
    main()