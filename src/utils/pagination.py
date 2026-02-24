from src.api.tmdb import search_tmdb, get_tmdb_total_pages
from src.api.omdb import get_omdb_ratings

def get_page_shufflers(args_type, genres, platforms, min_year):
    """
    Returns shuffled lists of pages for movies and tv series based on total TMDB counts.
    Limits to the first 500 pages (TMDB API max depth limit).
    """
    movie_pages = get_tmdb_total_pages('movie', genres, platforms, min_year) if args_type in ('movie', 'both') else 0
    tv_pages = get_tmdb_total_pages('tv', genres, platforms, min_year) if args_type in ('tv', 'both') else 0
    
    max_movie_pages = min(movie_pages, 500)
    max_tv_pages = min(tv_pages, 500)
    
    movie_page_list = list(range(1, max_movie_pages + 1)) if max_movie_pages > 0 else []
    tv_page_list = list(range(1, max_tv_pages + 1)) if max_tv_pages > 0 else []
    
    return movie_page_list, tv_page_list


def fetch_shuffled_page(rng, requested_page, items_per_page, media_type_pref, genres, platforms, min_year, watched_ids, include_watched):
    """
    Orchestrates deep pagination, shuffling, interleaving, and rigorous valid-result
    filtering across TMDB and OMDB to yield precisely the block of results requested.
    """
    movie_page_list, tv_page_list = get_page_shufflers(media_type_pref, genres, platforms, min_year)
    
    if movie_page_list: rng.shuffle(movie_page_list)
    if tv_page_list: rng.shuffle(tv_page_list)
    
    target_count = requested_page * items_per_page
    attempts = 0
    MAX_ATTEMPTS = 150
    valid_results = []
    
    while len(valid_results) < target_count and attempts < MAX_ATTEMPTS and (movie_page_list or tv_page_list):
        attempts += 1
        
        movies = []
        if media_type_pref in ('movie', 'both') and movie_page_list:
            current_movie_page = movie_page_list.pop(0)
            movies = search_tmdb('movie', genres, platforms, current_movie_page, min_year)
            for m in movies: m['media_type'] = 'movie'
            
        shows = []
        if media_type_pref in ('tv', 'both') and tv_page_list:
            current_tv_page = tv_page_list.pop(0)
            shows = search_tmdb('tv', genres, platforms, current_tv_page, min_year)
            for s in shows: s['media_type'] = 'tv'
        
        # Interleave
        mixed = []
        for i in range(max(len(movies), len(shows))):
            if i < len(movies):
                mixed.append(movies[i])
            if i < len(shows):
                mixed.append(shows[i])
                
        if not mixed:
            continue
            
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
    start_idx = (requested_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    
    return valid_results[start_idx:end_idx]
