from src.config import GENRE_MAPPING
from src.api.tmdb import get_tmdb_details, get_watch_providers
from src.api.youtube import get_youtube_trailer

def build_media_card(item, omdb_ratings=None, tmdb_rating=None, user_genre_ids=None, language='en-US', region='US'):
    """
    Transforms a raw TMDB API item dictionary into the standard JSON
    'card' format expected by the bot instructions.

    Item should already have 'media_type', 'is_watched'.
    'omdb_ratings' and 'tmdb_rating' can be injected if pre-fetched.
    """
    title = item.get('title') or item.get('name')
    release_date = item.get('release_date') or item.get('first_air_date')
    year = release_date[:4] if release_date else ""

    trailer = get_youtube_trailer(f"{title} {year}", language=language, region=region)

    item_type = item.get('media_type', 'movie')
    item_id = item.get('id')

    # Fetch detailed credits and overview
    details = get_tmdb_details(item_id, item_type, language) or {}
    overview = details.get('overview') or item.get('overview') or ""

    credits_data = details.get('credits', {})
    cast = [c['name'] for c in credits_data.get('cast', [])[:3]]

    if item_type == 'movie':
        directors = [c['name'] for c in credits_data.get('crew', []) if c.get('job') == 'Director'][:2]
    else:
        directors = [c['name'] for c in credits_data.get('crew', []) if c.get('department') == 'Directing'][:2]

    genre_ids = item.get('genre_ids', [])
    user_genre_ids = user_genre_ids or []
    all_genre_names = [GENRE_MAPPING.get(gid, '') for gid in genre_ids if gid in GENRE_MAPPING]
    matched_genre_names = [GENRE_MAPPING.get(gid, '') for gid in genre_ids if gid in user_genre_ids and gid in GENRE_MAPPING]

    poster_path = item.get('poster_path') or details.get('poster_path')
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

    platform_objects = get_watch_providers(item_id, item_type, title, region)

    or_ratings = omdb_ratings or item.get('omdb_ratings', {})
    tr_rating = tmdb_rating or item.get('tmdb_rating', round(item.get('vote_average') or 0, 1))

    return {
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
            'tomatometer': or_ratings.get('tomatometer'),
            'imdb': or_ratings.get('imdb'),
            'metacritic': or_ratings.get('metacritic'),
            'tmdb': tr_rating
        },
        'platforms': platform_objects,
        'trailer_url': trailer,
        'poster_url': poster_url,
        'is_watched': item.get('is_watched', False)
    }
