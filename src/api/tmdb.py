import requests
from src.config import Config
from src.utils.platforms import build_platform_url, normalize_provider_name

def get_tmdb_total_pages(media_type, genres, providers, min_year=None):
    url = f"https://api.themoviedb.org/3/discover/{media_type}"
    params = {
        'api_key': Config.TMDB_API_KEY,
        'language': Config.LANGUAGE,
        'watch_region': Config.REGION,
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

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return min(data.get('total_pages', 1), 500)

def search_tmdb(media_type, genres, providers, page=1, min_year=None):
    url = f"https://api.themoviedb.org/3/discover/{media_type}"
    params = {
        'api_key': Config.TMDB_API_KEY,
        'language': Config.LANGUAGE,
        'watch_region': Config.REGION,
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

def get_tmdb_details(item_id, media_type):
    url = f"https://api.themoviedb.org/3/{media_type}/{item_id}"
    params = {'api_key': Config.TMDB_API_KEY, 'language': Config.LANGUAGE, 'append_to_response': 'credits'}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

def search_tmdb_by_title(query, media_type='multi'):
    # media_type can be 'multi', 'movie', or 'tv'
    url = f"https://api.themoviedb.org/3/search/{media_type}"
    params = {
        'api_key': Config.TMDB_API_KEY,
        'language': Config.LANGUAGE,
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

def get_watch_providers(item_id, media_type, title):
    """
    Fetch streaming providers for Italy from TMDB.
    Returns a unified list (no duplicates),
    where tier is 'subscription' (flatrate) or 'free' (free + ads).
    """
    url = f"https://api.themoviedb.org/3/{media_type}/{item_id}/watch/providers"
    params = {'api_key': Config.TMDB_API_KEY}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json().get('results', {})
            it_data = data.get(Config.REGION, {})
            platforms = []
            seen = set()

            # Subscription tier (flatrate)
            for p in it_data.get('flatrate', []):
                name = normalize_provider_name(p['provider_name'])
                if name not in seen:
                    seen.add(name)
                    platforms.append({'name': name, 'url': build_platform_url(name, title), 'tier': 'subscription'})

            # Free tier (no ads)
            for p in it_data.get('free', []):
                name = normalize_provider_name(p['provider_name'])
                if name not in seen:
                    seen.add(name)
                    platforms.append({'name': name, 'url': build_platform_url(name, title), 'tier': 'free'})

            # Free with ads tier
            for p in it_data.get('ads', []):
                name = normalize_provider_name(p['provider_name'])
                if name not in seen:
                    seen.add(name)
                    platforms.append({'name': name, 'url': build_platform_url(name, title), 'tier': 'ads'})

            return platforms
    except Exception:
        pass
    return []
