import os
import sys
import json
import argparse
import requests
from dotenv import load_dotenv

# We reuse the robust data fetching functions from search.py
from search import (
    TMDB_API_KEY, REGION, LANGUAGE, GENRE_MAPPING,
    get_omdb_ratings, get_tmdb_details,
    get_youtube_trailer, get_watch_providers
)

def search_by_title(query, media_type='multi'):
    # media_type can be 'multi', 'movie', or 'tv'
    url = f"https://api.themoviedb.org/3/search/{media_type}"
    params = {
        'api_key': TMDB_API_KEY,
        'language': LANGUAGE,
        'query': query,
        'page': 1
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get('results', [])
    except Exception:
        pass
    return []

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('query', type=str, help='Title to search for')
    parser.add_argument('--type', type=str, choices=['movie', 'tv', 'both'], default='both', help='Media type')
    args = parser.parse_args()
    
    # Map 'both' to 'multi' for TMDB search API
    search_type = 'multi' if args.type == 'both' else args.type
    
    raw_results = search_by_title(args.query, search_type)
    
    # Filter out people ('person' media type) if multi search is used
    valid_items = [item for item in raw_results if item.get('media_type') != 'person']
    
    # Take top 3
    top_items = valid_items[:3]
    
    final_output = []
    
    for item in top_items:
        # If we searched specifically for movie or tv, media_type might not be in the item dict
        item_type = item.get('media_type', args.type if args.type != 'both' else 'movie')
        
        title = item.get('title') or item.get('name')
        release_date = item.get('release_date') or item.get('first_air_date')
        year = release_date[:4] if release_date else ""
        
        tmdb_rating = round(item.get('vote_average') or 0, 1)
        omdb_ratings = get_omdb_ratings(title, year)
        
        trailer = get_youtube_trailer(f"{title} {year}")
        platforms_found = get_watch_providers(item.get('id'), item_type, title)
        
        poster_path = item.get('poster_path')
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
        
        item_genres = []
        for gid in item.get('genre_ids', []):
            gname = GENRE_MAPPING.get(gid, str(gid))
            item_genres.append(gname)
            
        details = get_tmdb_details(item.get('id'), item_type) or {}
        overview = details.get('overview') or item.get('overview') or ""
        
        credits_data = details.get('credits', {})
        cast = [c['name'] for c in credits_data.get('cast', [])[:3]]
        
        directors = []
        if item_type == 'movie':
            directors = [c['name'] for c in credits_data.get('crew', []) if c.get('job') == 'Director']
        else: # tv
            directors = [c['name'] for c in details.get('created_by', [])]
            
        final_output.append({
            'id': item.get('id'),
            'type': item_type,
            'title': title,
            'year': year,
            'overview': overview,
            'genres': item_genres,
            'matched_genres': [], # Not relevant for direct title search
            'directors': directors,
            'cast': cast,
            'ratings': {
                'tomatometer': omdb_ratings.get('tomatometer'),
                'imdb': omdb_ratings.get('imdb'),
                'metacritic': omdb_ratings.get('metacritic'),
                'tmdb': tmdb_rating
            },
            'platforms': platforms_found,
            'trailer_url': trailer,
            'poster_url': poster_url,
            'is_watched': False # Not tracking watched state tightly in direct search for now, leaving explicit toggle out of output to avoid confusing
        })
        
    print(json.dumps(final_output, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    if not TMDB_API_KEY:
        print(json.dumps({"error": "TMDB_API_KEY must be set in .env"}))
        sys.exit(1)
    main()
