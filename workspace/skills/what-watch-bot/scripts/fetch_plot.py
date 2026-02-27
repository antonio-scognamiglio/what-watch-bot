import os
import sys
import json

# Add project root to path so we can import 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import get_connection, get_prefs
from src.api.omdb import fetch_omdb_plot
from src.api.wikipedia import fetch_wikipedia_plot


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing title argument"}, indent=2))
        sys.exit(1)

    target_title = sys.argv[1]
    # Optional year and media_type help Wikipedia disambiguate (e.g. 'film' vs band)
    year = sys.argv[2] if len(sys.argv) >= 3 else None
    media_type = sys.argv[3] if len(sys.argv) >= 4 else None  # 'movie' | 'tv'

    # Read user language preference to determine fallback chain
    conn = get_connection()
    prefs = get_prefs(conn)
    language = prefs.get('language', 'en-US')

    # Extract the 2-letter Wikipedia language code (e.g., 'it' from 'it-IT', 'en' from 'en-US')
    wiki_lang = language.split('-')[0].lower()

    # Step 1: Try Wikipedia in the user's configured language (skip if already English)
    if wiki_lang != 'en':
        plot = fetch_wikipedia_plot(target_title, lang=wiki_lang, year=year, media_type=media_type)
        if plot:
            print(json.dumps({"plot": plot, "source": f"wikipedia_{wiki_lang}"}, ensure_ascii=False, indent=2))
            sys.exit(0)

    # Step 2: Try English Wikipedia
    plot_en = fetch_wikipedia_plot(target_title, lang="en", year=year, media_type=media_type)
    if plot_en:
        print(json.dumps({"plot": plot_en, "source": "wikipedia_en"}, ensure_ascii=False, indent=2))
        sys.exit(0)

    # Step 3: Fallback to OMDb (always English)
    omdb_plot = fetch_omdb_plot(target_title)
    if omdb_plot:
        print(json.dumps({"plot": omdb_plot, "source": "omdb_en"}, ensure_ascii=False, indent=2))
        sys.exit(0)

    print(json.dumps({"error": "Plot not found"}, indent=2))
