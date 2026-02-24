import random
from src.api.tmdb import search_tmdb, get_tmdb_total_pages
from src.api.omdb import get_omdb_ratings
from src.database import load_cache, save_cache


def _build_page_lists(media_type_pref, genres, platforms, min_year, language, region, rng):
    """Fetch total TMDB pages and return shuffled lists for movie and tv."""
    movie_pages = (
        get_tmdb_total_pages('movie', genres, platforms, min_year, language, region)
        if media_type_pref in ('movie', 'both') else 0
    )
    tv_pages = (
        get_tmdb_total_pages('tv', genres, platforms, min_year, language, region)
        if media_type_pref in ('tv', 'both') else 0
    )
    movie_list = list(range(1, min(movie_pages, 500) + 1))
    tv_list = list(range(1, min(tv_pages, 500) + 1))
    if movie_list: rng.shuffle(movie_list)
    if tv_list: rng.shuffle(tv_list)
    return movie_list, tv_list


def _fetch_and_filter(media_type_pref, genres, platforms, min_year, language, region,
                      watched_ids, include_watched, rt_min_score,
                      tmdb_pages_movie, tmdb_pages_tv, rng, target_count, current_pool):
    """
    Continue fetching from TMDB (using the remaining page queues) until
    current_pool has at least target_count items, or TMDB is exhausted.
    Returns (updated_pool, updated_movie_pages, updated_tv_pages, exhausted).
    """
    MAX_ATTEMPTS = 150
    attempts = 0
    pool = list(current_pool)

    while len(pool) < target_count and attempts < MAX_ATTEMPTS and (tmdb_pages_movie or tmdb_pages_tv):
        attempts += 1

        movies = []
        if media_type_pref in ('movie', 'both') and tmdb_pages_movie:
            page = tmdb_pages_movie.pop(0)
            movies = search_tmdb('movie', genres, platforms, page, min_year, language, region)
            for m in movies:
                m['media_type'] = 'movie'

        shows = []
        if media_type_pref in ('tv', 'both') and tmdb_pages_tv:
            page = tmdb_pages_tv.pop(0)
            shows = search_tmdb('tv', genres, platforms, page, min_year, language, region)
            for s in shows:
                s['media_type'] = 'tv'

        mixed = []
        for i in range(max(len(movies), len(shows))):
            if i < len(movies): mixed.append(movies[i])
            if i < len(shows): mixed.append(shows[i])

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

            if tmdb_rating >= 7.0 or toma >= rt_min_score or imdb >= 7.0 or meta >= rt_min_score:
                item['omdb_ratings'] = omdb_ratings
                item['tmdb_rating'] = tmdb_rating
                item['is_watched'] = is_watched
                pool.append(item)

    exhausted = not tmdb_pages_movie and not tmdb_pages_tv
    return pool, tmdb_pages_movie, tmdb_pages_tv, exhausted


def fetch_page_from_cache(conn, cache_key, items_per_page, seed, media_type_pref,
                          genres, platforms, min_year, watched_ids, include_watched,
                          language, region, rt_min_score):
    """
    Main entry point for cached pagination.

    Loads the cache for this (seed + prefs) session, refills the pool from TMDB
    if needed, pops the first `items_per_page` items, persists the updated state,
    and returns the page results.
    """
    rng = random.Random(seed)
    state = load_cache(conn, cache_key)

    if state is None:
        # Cold start — build the shuffled TMDB page lists
        movie_list, tv_list = _build_page_lists(
            media_type_pref, genres, platforms, min_year, language, region, rng
        )
        pool = []
        exhausted = False
        created_at = None  # save_cache will set current timestamp
    else:
        pool = state['pool']
        movie_list = state['tmdb_pages_movie']
        tv_list = state['tmdb_pages_tv']
        exhausted = state['exhausted']
        created_at = state['created_at']
        # Re-seed rng — it's only used for shuffling new TMDB results
        # (the page ordering is already persisted, rng is stateless here)

    # Refill pool if needed and TMDB is not exhausted
    if len(pool) < items_per_page and not exhausted:
        pool, movie_list, tv_list, exhausted = _fetch_and_filter(
            media_type_pref, genres, platforms, min_year, language, region,
            watched_ids, include_watched, rt_min_score,
            movie_list, tv_list, rng, items_per_page, pool
        )

    # Pop the page from the front of the pool
    page_results = pool[:items_per_page]
    remaining_pool = pool[items_per_page:]

    # Persist updated state (keep original created_at to respect TTL correctly)
    save_cache(conn, cache_key, remaining_pool, movie_list, tv_list, exhausted, created_at)

    return page_results


# ── Legacy helper kept for backward compatibility (not used by search.py anymore) ───────
def fetch_shuffled_page(rng, requested_page, items_per_page, media_type_pref,
                        genres, platforms, min_year, watched_ids, include_watched,
                        language='en-US', region='US', rt_min_score=70):
    """Stateless fallback (no cache). Used by tests or direct calls."""
    movie_list, tv_list = _build_page_lists(
        media_type_pref, genres, platforms, min_year, language, region, rng
    )
    target_count = requested_page * items_per_page
    pool, _, _, _ = _fetch_and_filter(
        media_type_pref, genres, platforms, min_year, language, region,
        watched_ids, include_watched, rt_min_score,
        movie_list, tv_list, rng, target_count, []
    )
    start = (requested_page - 1) * items_per_page
    return pool[start:start + items_per_page]
