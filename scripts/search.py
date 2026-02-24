import os
import sys
import json
import argparse
import random

# Add project root to path so we can import 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import get_connection, get_prefs, get_watched_ids, make_cache_key
from src.utils.pagination import fetch_page_from_cache
from src.utils.formatters import build_media_card


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--page', type=int, default=1, help='Page number (ignored with cache, kept for compatibility)')
    parser.add_argument('--type', type=str, choices=['movie', 'tv', 'both'], default='both', help='Media type to search')
    parser.add_argument('--seed', type=int, default=None, help='Seed for the search session')
    args = parser.parse_args()

    conn = get_connection()
    prefs = get_prefs(conn)
    watched_ids = get_watched_ids(conn)

    genres = prefs.get('genres', [])
    platforms = prefs.get('platforms', [])
    include_watched = prefs.get('include_watched', False)
    min_year = prefs.get('min_year')
    language = prefs.get('language', 'en-US')
    region = prefs.get('region', 'US')
    rt_min_score = prefs.get('rt_min_score', 70)
    items_per_page = prefs.get('max_results', 5)

    seed = args.seed if args.seed is not None else random.randint(1000, 9999)

    # Build a cache key that encodes seed + type + all relevant prefs
    cache_key = make_cache_key(seed, args.type, prefs)

    # Fetch page from the persistent cache queue (refills from TMDB only when needed)
    page_results = fetch_page_from_cache(
        conn=conn,
        cache_key=cache_key,
        items_per_page=items_per_page,
        seed=seed,
        media_type_pref=args.type,
        genres=genres,
        platforms=platforms,
        min_year=min_year,
        watched_ids=watched_ids,
        include_watched=include_watched,
        language=language,
        region=region,
        rt_min_score=rt_min_score,
    )

    # Enrich with trailers, platforms, and format output
    final_output = [
        build_media_card(item, user_genre_ids=genres, language=language, region=region)
        for item in page_results
    ]

    print(json.dumps(final_output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
