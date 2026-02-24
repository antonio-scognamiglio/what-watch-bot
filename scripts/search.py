import os
import sys
import json
import argparse
import random

# Add project root to path so we can import 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import get_connection, get_prefs, get_watched_ids
from src.utils.pagination import fetch_shuffled_page
from src.utils.formatters import build_media_card


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
    
    # Fetch the exact page of items we need
    page_results = fetch_shuffled_page(rng, args.page, ITEMS_PER_PAGE, args.type, genres, platforms, min_year, watched_ids, include_watched)
    
    # Enrich with trailers, platforms, and format output
    final_output = [build_media_card(item, user_genre_ids=genres) for item in page_results]
    
    print(json.dumps(final_output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
