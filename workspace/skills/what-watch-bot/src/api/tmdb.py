import requests
from src.config import Config
from src.utils.platforms import build_platform_url, normalize_provider_name, _PLATFORM_URL_BUILDERS
from src.utils.logger import get_logger

logger = get_logger(__name__)

def get_tmdb_total_pages(media_type, genres, providers, rent_buy=False, min_year=None, language='en-US', region='US'):
    url = f"https://api.themoviedb.org/3/discover/{media_type}"
    params = {
        'api_key': Config.TMDB_API_KEY,
        'language': language,
        'watch_region': region,
        'with_watch_providers': '|'.join(map(str, providers)) if providers else '',
        'with_watch_monetization_types': 'flatrate|free|ads|rent|buy' if rent_buy else 'flatrate|free|ads',
        'with_genres': '|'.join(map(str, genres)) if genres else '',
        'sort_by': 'popularity.desc',
        'page': 1
    }

    if min_year:
        if media_type == 'movie':
            params['primary_release_date.gte'] = f"{min_year}-01-01"
        else:
            params['first_air_date.gte'] = f"{min_year}-01-01"

    logger.info(f"Fetching TMDB total pages for {media_type}")
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    total_pages = min(data.get('total_pages', 1), 500)
    logger.info(f"TMDB total pages: {total_pages}")
    return total_pages

def search_tmdb(media_type, genres, providers, rent_buy=False, page=1, min_year=None, language='en-US', region='US'):
    url = f"https://api.themoviedb.org/3/discover/{media_type}"
    params = {
        'api_key': Config.TMDB_API_KEY,
        'language': language,
        'watch_region': region,
        'with_watch_providers': '|'.join(map(str, providers)) if providers else '',
        'with_watch_monetization_types': 'flatrate|free|ads|rent|buy' if rent_buy else 'flatrate|free|ads',
        'with_genres': '|'.join(map(str, genres)) if genres else '',
        'sort_by': 'popularity.desc',
        'page': page
    }

    if min_year:
        if media_type == 'movie':
            params['primary_release_date.gte'] = f"{min_year}-01-01"
        else:
            params['first_air_date.gte'] = f"{min_year}-01-01"

    logger.info(f"Searching TMDB for {media_type} (page {page}, min_year={min_year})")
    response = requests.get(url, params=params)
    response.raise_for_status()
    results = response.json().get('results', [])
    logger.info(f"Found {len(results)} items from TMDB discovery")
    return results

def get_tmdb_details(item_id, media_type, language='en-US'):
    url = f"https://api.themoviedb.org/3/{media_type}/{item_id}"
    params = {'api_key': Config.TMDB_API_KEY, 'language': language, 'append_to_response': 'credits'}
    try:
        logger.info(f"Fetching TMDB details for {media_type} {item_id}")
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        logger.warning(f"Failed to fetch details for {media_type} {item_id}: status {response.status_code}")
    except Exception as e:
        logger.error(f"Error fetching TMDB details for {media_type} {item_id}: {e}")
    return None

def search_tmdb_by_title(query, media_type='multi', language='en-US'):
    url = f"https://api.themoviedb.org/3/search/{media_type}"
    params = {
        'api_key': Config.TMDB_API_KEY,
        'language': language,
        'query': query,
        'page': 1
    }
    try:
        logger.info(f"Searching TMDB by title: '{query}' ({media_type})")
        response = requests.get(url, params=params)
        if response.status_code == 200:
            results = response.json().get('results', [])
            logger.info(f"Found {len(results)} results for title search")
            return results
        logger.warning(f"Title search failed for '{query}': status {response.status_code}")
    except Exception as e:
        logger.error(f"Error searching TMDB by title '{query}': {e}")
    return []

def get_watch_providers(item_id, media_type, title, region='US', rent_buy=False, show_all=False):
    """
    Fetch streaming providers for a given region from TMDB.
    Returns a unified list (no duplicates).

    show_all=False (default, used by suggest): only return providers in the supported registry.
    show_all=True (used by find_title): return ALL providers in the region. Known providers
    get a clickable URL; unknown providers are included with url=None (name only).
    """
    url = f"https://api.themoviedb.org/3/{media_type}/{item_id}/watch/providers"
    params = {'api_key': Config.TMDB_API_KEY}
    try:
        logger.info(f"Fetching watch providers for {media_type} {item_id}")
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json().get('results', {})
            region_data = data.get(region, {})
            platforms = []
            seen = set()

            for tier_key, tier_name in [('flatrate', 'subscription'), ('free', 'free'), ('ads', 'ads')]:
                for p in region_data.get(tier_key, []):
                    normalized = normalize_provider_name(p['provider_name'])
                    key = normalized or p['provider_name']
                    if key in seen:
                        continue
                    seen.add(key)
                    if normalized in _PLATFORM_URL_BUILDERS:
                        platforms.append({'name': normalized, 'url': build_platform_url(p['provider_name'], title), 'tier': tier_name})
                    elif show_all:
                        platforms.append({'name': p['provider_name'], 'url': None, 'tier': tier_name})

            if rent_buy:
                for tier_key, tier_name in [('rent', 'rent'), ('buy', 'buy')]:
                    for p in region_data.get(tier_key, []):
                        normalized = normalize_provider_name(p['provider_name'])
                        key = normalized or p['provider_name']
                        if key in seen:
                            continue
                        seen.add(key)
                        if normalized in _PLATFORM_URL_BUILDERS:
                            platforms.append({'name': normalized, 'url': build_platform_url(p['provider_name'], title), 'tier': tier_name})
                        elif show_all:
                            platforms.append({'name': p['provider_name'], 'url': None, 'tier': tier_name})

            logger.info(f"Found {len(platforms)} providers for {title} in {region} (show_all={show_all})")
            return platforms
        logger.warning(f"Watch provider lookup failed for {media_type} {item_id}: status {response.status_code}")
    except Exception as e:
        logger.error(f"Error fetching watch providers for {media_type} {item_id}: {e}")
    return []
