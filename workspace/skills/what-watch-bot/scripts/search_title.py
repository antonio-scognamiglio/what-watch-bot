import os
import sys
import json
import argparse

# Add project root to path so we can import 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import Config
from src.database import get_connection, get_prefs
from src.api.tmdb import search_tmdb_by_title
from src.utils.formatters import build_media_card

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('query', type=str, help='Title to search for')
    parser.add_argument('--type', type=str, choices=['movie', 'tv', 'both'], default='both', help='Media type')
    args = parser.parse_args()

    conn = get_connection()
    prefs = get_prefs(conn)
    language = prefs.get('language', 'en-US')
    region = prefs.get('region', 'US')

    # Map 'both' to 'multi' for TMDB search API
    search_type = 'multi' if args.type == 'both' else args.type

    raw_results = search_tmdb_by_title(args.query, search_type, language=language)

    # Filter out people ('person' media type) if multi search is used
    valid_items = [item for item in raw_results if item.get('media_type') != 'person']

    # Take top 3
    top_items = valid_items[:3]

    final_output = []
    for item in top_items:
        # Guarantee media_type exists for the formatter if we forced a specific search
        if 'media_type' not in item:
            item['media_type'] = args.type if args.type != 'both' else 'movie'

        card = build_media_card(item, language=language, region=region, show_all=True)
        final_output.append(card)

    print(json.dumps(final_output, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    if not Config.TMDB_API_KEY:
        print(json.dumps({"error": "TMDB_API_KEY must be set in .env"}))
        sys.exit(1)
    main()
