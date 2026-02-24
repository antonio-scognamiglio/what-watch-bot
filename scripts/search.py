import os
import sys
import json
import argparse
import random

# Add project root to path so we can import 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import get_connection, get_prefs, get_watched_ids
from src.config import Config, GENRE_MAPPING
from src.api.tmdb import get_tmdb_total_pages, search_tmdb, get_tmdb_details, get_watch_providers
from src.api.omdb import get_omdb_ratings
from src.api.youtube import get_youtube_trailer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--page', type=int, default=1, help='Page number to fetch')
    parser.add_argument('--type', type=str, choices=['movie', 'tv', 'both'], default='both', help='Media type to search')
    parser.add_argument('--seed', type=int, default=None, help='Seed for deterministic deep paging shuffle')
    args = parser.parse_args()
    # Initialize DB (which also initializes tables if missing)
    conn = get_connection()
    prefs = get_prefs(conn)
    watched_ids = get_watched_ids(conn)
    
    genres = prefs.get('genres', [])
    platforms = prefs.get('platforms', [])
    include_watched = prefs.get('include_watched', False)
    min_year = prefs.get('min_year')
    ITEMS_PER_PAGE = prefs.get('max_results', 5)
    
    # Establish Random Generator
    rng = random.Random(args.seed if args.seed is not None else 42)
    
    # Pre-fetch total pages to set our deep shuffle bounds
    movie_pages = get_tmdb_total_pages('movie', genres, platforms, min_year) if args.type in ('movie', 'both') else 0
    tv_pages = get_tmdb_total_pages('tv', genres, platforms, min_year) if args.type in ('tv', 'both') else 0
    
    # TMDB limits deep paging to 500
    max_movie_pages = min(movie_pages, 500)
    max_tv_pages = min(tv_pages, 500)
    
    movie_page_list = list(range(1, max_movie_pages + 1)) if max_movie_pages > 0 else []
    tv_page_list = list(range(1, max_tv_pages + 1)) if max_tv_pages > 0 else []
    
    # Deterministically shuffle the pages
    if movie_page_list: rng.shuffle(movie_page_list)
    if tv_page_list: rng.shuffle(tv_page_list)
    
    # Our target valid items to collect before returning exactly the requested page slice
    target_count = args.page * ITEMS_PER_PAGE
    
    # Track how many TMDB pages we tried to avoid infinite loops if constraints are too tight
    attempts = 0
    MAX_ATTEMPTS = 150
    
    valid_results = []
    
    while len(valid_results) < target_count and attempts < MAX_ATTEMPTS and (movie_page_list or tv_page_list):
        attempts += 1
        
        movies = []
        if args.type in ('movie', 'both') and movie_page_list:
            current_movie_page = movie_page_list.pop(0)
            movies = search_tmdb('movie', genres, platforms, current_movie_page, min_year)
            for m in movies: m['media_type'] = 'movie'
            
        shows = []
        if args.type in ('tv', 'both') and tv_page_list:
            current_tv_page = tv_page_list.pop(0)
            shows = search_tmdb('tv', genres, platforms, current_tv_page, min_year)
            for s in shows: s['media_type'] = 'tv'
        
        # Interleave or append
        mixed = []
        for i in range(max(len(movies), len(shows))):
            if i < len(movies):
                mixed.append(movies[i])
            if i < len(shows):
                mixed.append(shows[i])
                
        if not mixed:
            continue
            
        # Deterministically shuffle the items on this page so we don't always favor top popularity 
        rng.shuffle(mixed)
            
        for item in mixed:
            item_id = item.get('id')
            is_watched = item_id in watched_ids
            if is_watched and not include_watched:
                continue
                
            title = item.get('title') or item.get('name')
            release_date = item.get('release_date') or item.get('first_air_date')
            year = release_date[:4] if release_date else None
            
            tmdb_rating = round(item.get('vote_average') or 0, 1)
            omdb_ratings = get_omdb_ratings(title, year)
            
            toma = omdb_ratings.get('tomatometer') or 0
            imdb = omdb_ratings.get('imdb') or 0
            meta = omdb_ratings.get('metacritic') or 0
            
            # OR logic: if any of the ratings meets the threshold
            if tmdb_rating >= 7.0 or toma >= 70 or imdb >= 7.0 or meta >= 70:
                item['omdb_ratings'] = omdb_ratings
                item['tmdb_rating'] = tmdb_rating
                item['is_watched'] = is_watched
                valid_results.append(item)
                
            if len(valid_results) >= target_count:
                break
        
    # Get the slice for the requested page
    start_idx = (args.page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_results = valid_results[start_idx:end_idx]
    
    # Enrich with trailers and platforms
    final_output = []
    for item in page_results:
        title = item.get('title') or item.get('name')
        release_date = item.get('release_date') or item.get('first_air_date')
        year = release_date[:4] if release_date else ""
        
        trailer = get_youtube_trailer(f"{title} {year}")
        
        item_type = item.get('media_type', 'movie')
        item_id = item.get('id')
        
        # Fetch detailed credits and overview
        details = get_tmdb_details(item.get('id'), item.get('media_type')) or {}
        overview = details.get('overview') or item.get('overview') or ""
        
        credits_data = details.get('credits', {})
        cast = [c['name'] for c in credits_data.get('cast', [])[:3]]
        
        if item_type == 'movie':
            directors = [c['name'] for c in credits_data.get('crew', []) if c.get('job') == 'Director'][:2]
        else:
            directors = [c['name'] for c in credits_data.get('crew', []) if c.get('department') == 'Directing'][:2]

        genre_ids = item.get('genre_ids', [])
        user_genre_ids = prefs.get('genres', [])
        all_genre_names = [GENRE_MAPPING.get(gid, '') for gid in genre_ids if gid in GENRE_MAPPING]
        matched_genre_names = [GENRE_MAPPING.get(gid, '') for gid in genre_ids if gid in user_genre_ids and gid in GENRE_MAPPING]
        
        poster_path = item.get('poster_path') or details.get('poster_path')
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
        
        platform_objects = get_watch_providers(item_id, item_type, title)
        
        omdb_ratings = item.get('omdb_ratings', {})
        tmdb_rating = item.get('tmdb_rating', 0)
        
        final_output.append({
            'id': item_id,
            'type': item_type,
            'title': title,
            'year': year,
            'overview': overview,
            'genres': [g for g in all_genre_names if g],
            'matched_genres': [g for g in matched_genre_names if g],
            'directors': directors,
            'cast': cast,
            'ratings': {
                'tomatometer': omdb_ratings.get('tomatometer'),
                'imdb': omdb_ratings.get('imdb'),
                'metacritic': omdb_ratings.get('metacritic'),
                'tmdb': tmdb_rating
            },
            'platforms': platform_objects,
            'trailer_url': trailer,
            'poster_url': poster_url,
            'is_watched': item.get('is_watched', False)
        })
    
    print(json.dumps(final_output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
