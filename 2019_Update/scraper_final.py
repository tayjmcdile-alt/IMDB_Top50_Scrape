import requests
from bs4 import BeautifulSoup
import json
import datetime
import os
from time import sleep

def get_movie_data(year):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    
    url = f"https://www.imdb.com/search/title/?title_type=feature&release_date={year}&sort=num_votes,desc&count=50"
    print(f"\nFetching movies for year {year}...")
    
    try:
        session = requests.Session()
        response = session.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        movies = []
        
        # Find all movie containers
        movie_containers = soup.select('div.lister-item.mode-advanced')
        
        if not movie_containers:
            print(f"No movies found for {year}. Saving response for debugging...")
            with open('debug_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            return None
            
        for i, container in enumerate(movie_containers[:50], 1):
            movie = {}
            
            # Get title
            header = container.select_one('.lister-item-header a')
            if header:
                movie['name'] = header.text.strip()
            
            # Get year, runtime, genre from the muted text
            muted_text = container.select_one('.text-muted')
            if muted_text:
                # Certificate
                certificate = container.select_one('.certificate')
                movie['certificate'] = certificate.text.strip() if certificate else ''
                
                # Runtime
                runtime = container.select_one('.runtime')
                movie['runtime'] = runtime.text.strip() if runtime else ''
                
                # Genre
                genre = container.select_one('.genre')
                movie['genre'] = genre.text.strip() if genre else ''
            
            # Get description
            description = container.select('p.text-muted')
            if len(description) > 1:
                movie['description'] = description[1].text.strip()
            else:
                movie['description'] = ''
            
            # Get director and stars
            credits = container.select_one('p:not(.text-muted)')
            if credits:
                credit_text = credits.text.strip()
                
                # Try to parse director and stars
                if 'Director:' in credit_text:
                    director_part = credit_text.split('Stars:')[0]
                    movie['director'] = director_part.replace('Director:', '').strip()
                    
                    # Get stars
                    if 'Stars:' in credit_text:
                        stars_part = credit_text.split('Stars:')[1]
                        movie['stars'] = [s.strip() for s in stars_part.split('|')]
                    else:
                        movie['stars'] = []
                else:
                    movie['director'] = ''
                    movie['stars'] = []
            
            print(f"[{i}/50] Processed: {movie.get('name', 'Unknown Title')}")
            movies.append(movie)
            
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