import requests
from bs4 import BeautifulSoup
import json
import datetime
import os
from time import sleep

def get_movie_data(year):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    url = f"https://www.imdb.com/search/title/?title_type=feature&year={year}&sort=num_votes,desc"
    print(f"\nFetching movies for year {year}...")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        soup = BeautifulSoup(response.text, 'html.parser')
        movies = []
        
        # Find all movie containers
        movie_containers = soup.find_all('div', class_='lister-item-content')
        
        if not movie_containers:
            print(f"No movies found for {year}. The page structure might have changed.")
            return None
            
        for i, container in enumerate(movie_containers[:50], 1):
            movie = {}
            
            # Get title
            title_element = container.find('h3', class_='lister-item-header')
            if title_element and title_element.a:
                movie['name'] = title_element.a.text.strip()
            
            # Get year, runtime, genre
            info_element = container.find('p', class_='text-muted')
            if info_element:
                # Certificate
                certificate = info_element.find('span', class_='certificate')
                movie['certificate'] = certificate.text.strip() if certificate else ''
                
                # Runtime
                runtime = info_element.find('span', class_='runtime')
                movie['runtime'] = runtime.text.strip() if runtime else ''
                
                # Genre
                genre = info_element.find('span', class_='genre')
                movie['genre'] = genre.text.strip() if genre else ''
            
            # Get description
            description = container.find_all('p', class_='text-muted')
            if len(description) > 1:
                movie['description'] = description[1].text.strip()
            else:
                movie['description'] = ''
            
            # Get director and stars
            credits = container.find('p', class_='')
            if credits:
                director_element = credits.find('a')
                if director_element:
                    movie['director'] = director_element.text.strip()
                
                # Get stars
                stars = []
                for star in credits.find_all('a')[1:]:  # Skip first element (director)
                    stars.append(star.text.strip())
                movie['stars'] = stars
            
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