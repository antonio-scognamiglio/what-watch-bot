import os
import sys
import json
import argparse
import requests
import random
from urllib.parse import quote_plus
from dotenv import load_dotenv
import db_helper

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)

TMDB_API_KEY = os.getenv('TMDB_API_KEY')
OMDB_API_KEY = os.getenv('OMDB_API_KEY')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
RT_MIN_SCORE = int(os.getenv('RT_MIN_SCORE', '70'))
REGION = os.getenv('REGION', 'IT')
LANGUAGE = os.getenv('LANGUAGE', 'it-IT')

ITEMS_PER_PAGE = 5

# Provider IDs that are free or AVOD (no subscription needed)
FREE_PROVIDER_IDS = {35, 300, 192, 531, 538, 11, 339, 235}

# Names of known AVOD/free-with-ads platforms that TMDB may misclassify under flatrate
KNOWN_FREE_BY_NAME = {
    "amazon prime video with ads",
    "youtube free",
    "pluto tv",
    "tubi tv",
    "plex",
    "rakuten tv",
    "raiplay",
    "mediaset infinity free",
}

# Search URL templates for platforms (text-based deeplinks)
PLATFORM_SEARCH_URLS = {
    "Netflix":               "https://www.netflix.com/search?q={title}",
    "Amazon Prime Video":    "https://www.amazon.it/s?k={title}&i=instant-video",
    "Disney+":               "https://www.disneyplus.com/search/{title}",
    "Apple TV+":             "https://tv.apple.com/it/search?term={title}",
    "NOW TV":                "https://www.nowtv.it/ricerca?q={title}",
    "Rakuten TV":            "https://www.rakuten.tv/it/search?q={title}",
    "Mediaset Infinity":     "https://mediasetinfinity.mediaset.it/search/keyword/{title}",
    "RaiPlay":               "https://www.raiplay.it/ricerca.html#{title}",
    "Pluto TV":              "https://pluto.tv/it/search?q={title}",
    "Plex":                  "https://app.plex.tv/desktop/#!/search?query={title}",
    "MUBI":                  "https://mubi.com/it/search?query={title}",
    "YouTube":               "https://www.youtube.com/results?search_query={title}",
    "YouTube Premium":       "https://www.youtube.com/results?search_query={title}",
    "Paramount+":            "https://www.paramountplus.com/it/search/{title}/",
    "Infinity Selection Amazon Channel": "https://www.amazon.it/s?k={title}&i=instant-video",
    "Amazon Prime Video with Ads": "https://www.amazon.it/s?k={title}&i=instant-video",
}

def build_platform_url(name, title):
    template = PLATFORM_SEARCH_URLS.get(name)
    if template:
        return template.replace("{title}", quote_plus(title))
    return None

def get_tmdb_total_pages(media_type, genres, providers, min_year=None):
    url = f"https://api.themoviedb.org/3/discover/{media_type}"
    params = {
        'api_key': TMDB_API_KEY,
        'language': LANGUAGE,
        'watch_region': REGION,
        'with_watch_providers': '|'.join(map(str, providers)) if providers else '',
        'with_genres': '|'.join(map(str, genres)) if genres else '',
        'sort_by': 'popularity.desc', 
        'page': 1
    }
    
    if min_year:
        if media_type == 'movie':
            params['primary_release_date.gte'] = f"{min_year}-01-01"
        else:
            params['first_air_date.gte'] = f"{min_year}-01-01"
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get('total_pages', 1)
    except Exception:
        pass
    return 1

def search_tmdb(media_type, genres, providers, page=1, min_year=None):
    url = f"https://api.themoviedb.org/3/discover/{media_type}"
    params = {
        'api_key': TMDB_API_KEY,
        'language': LANGUAGE,
        'watch_region': REGION,
        'with_watch_providers': '|'.join(map(str, providers)) if providers else '',
        'with_genres': '|'.join(map(str, genres)) if genres else '',
        'sort_by': 'popularity.desc',
        'page': page
    }
    
    if min_year:
        if media_type == 'movie':
            params['primary_release_date.gte'] = f"{min_year}-01-01"
        else:
            params['first_air_date.gte'] = f"{min_year}-01-01"
            
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get('results', [])

GENRE_MAPPING = {
    28: 'Azione', 12: 'Avventura', 16: 'Animazione', 35: 'Commedia', 
    80: 'Crime', 99: 'Documentario', 18: 'Dramma', 10751: 'Famiglia', 
    14: 'Fantasy', 36: 'Storia', 27: 'Horror', 10402: 'Musica', 
    9648: 'Mistero', 10749: 'Romantico', 878: 'Fantascienza', 
    53: 'Thriller', 10752: 'Guerra', 37: 'Western',
    10759: 'Azione e Avventura', 10762: 'Kids', 10763: 'News', 
    10764: 'Reality', 10765: 'Sci-Fi e Fantasy', 10766: 'Soap', 
    10767: 'Talk', 10768: 'Guerra e Politica'
}

def get_omdb_ratings(title, year=None):
    if not OMDB_API_KEY:
        return {}
    url = "http://www.omdbapi.com/"
    params = {'apikey': OMDB_API_KEY, 't': title}
    if year:
        params['y'] = year
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code != 200:
            return {}
        data = response.json()
        if data.get('Response') == 'False':
            return {}
    except Exception:
        return {}
    
    ratings_dict = {}
    try:
        imdb_val = float(data.get('imdbRating', '0'))
        if imdb_val > 0: ratings_dict['imdb'] = imdb_val
    except ValueError:
        pass
    try:
        meta_val = int(data.get('Metascore', '0'))
        if meta_val > 0: ratings_dict['metacritic'] = meta_val
    except ValueError:
        pass
        
    ratings = data.get('Ratings', [])
    for rating in ratings:
        if rating.get('Source') == 'Rotten Tomatoes':
            val = rating.get('Value', '')
            if '%' in val:
                try: ratings_dict['tomatometer'] = int(val.replace('%', ''))
                except ValueError: pass
                
    return ratings_dict

def get_tmdb_details(item_id, media_type):
    url = f"https://api.themoviedb.org/3/{media_type}/{item_id}"
    params = {'api_key': TMDB_API_KEY, 'language': LANGUAGE, 'append_to_response': 'credits'}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None


def get_youtube_trailer(query):
    if not YOUTUBE_API_KEY:
        return None
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'key': YOUTUBE_API_KEY,
        'q': f"{query} trailer ufficiale",
        'part': 'snippet',
        'type': 'video',
        'maxResults': 1
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            items = response.json().get('items', [])
            if items:
                vid_id = items[0]['id']['videoId']
                return f"https://www.youtube.com/watch?v={vid_id}"
    except Exception:
        pass
    return None

def get_watch_providers(item_id, media_type, title):
    """
    Returns a list of platform objects:
    { name, url, tier }
    where tier is 'subscription' (flatrate) or 'free' (free + ads).
    """
    url = f"https://api.themoviedb.org/3/{media_type}/{item_id}/watch/providers"
    params = {'api_key': TMDB_API_KEY}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json().get('results', {})
            it_data = data.get(REGION, {})
            platforms = []
            seen = set()

            # Subscription (flatrate) — but some AVOD platforms land here too
            for p in it_data.get('flatrate', []):
                name = p['provider_name']
                if name not in seen:
                    seen.add(name)
                    tier = 'free' if name.lower() in KNOWN_FREE_BY_NAME else 'subscription'
                    platforms.append({
                        'name': name,
                        'url': build_platform_url(name, title),
                        'tier': tier
                    })

            # Free (free + ads → treated as same "free" category)
            for tier_key in ('free', 'ads'):
                for p in it_data.get(tier_key, []):
                    name = p['provider_name']
                    if name not in seen:
                        seen.add(name)
                        platforms.append({
                            'name': name,
                            'url': build_platform_url(name, title),
                            'tier': 'free'
                        })

            return platforms
    except Exception:
        pass
    return []

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--page', type=int, default=1, help='Page number to fetch')
    parser.add_argument('--type', type=str, choices=['movie', 'tv', 'both'], default='both', help='Media type to search')
    parser.add_argument('--seed', type=int, default=None, help='Seed for deterministic deep paging shuffle')
    args = parser.parse_args()
    
    conn = db_helper.get_connection()
    prefs = db_helper.get_prefs(conn)
    watched_ids = db_helper.get_watched_ids(conn)
    
    genres = prefs.get('genres', [])
    platforms = prefs.get('platforms', [])
    include_watched = prefs.get('include_watched', False)
    min_year = prefs.get('min_year')
    
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
