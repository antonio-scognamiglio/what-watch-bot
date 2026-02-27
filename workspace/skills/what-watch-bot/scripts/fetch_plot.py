import os
import sys
import json

# Add project root to path so we can import 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.omdb import fetch_omdb_plot


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing title argument"}, indent=2))
        sys.exit(1)

    target_title = sys.argv[1]

    # Try OMDb as last-resort plot source (TMDB English fallback is handled upstream)
    omdb_plot = fetch_omdb_plot(target_title)
    if omdb_plot:
        print(json.dumps({"plot": omdb_plot, "source": "omdb_en"}, ensure_ascii=False, indent=2))
        sys.exit(0)

    print(json.dumps({"error": "Plot not found"}, indent=2))
