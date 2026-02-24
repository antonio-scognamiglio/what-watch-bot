import os
import sys
import json

# Add project root to path so we can import 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.omdb import fetch_omdb_plot
from src.api.wikipedia import fetch_wikipedia_plot


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing title argument"}, indent=2))
        sys.exit(1)
        
    target_title = sys.argv[1]
    
    # Try OMDB first (most reliable for movies/TV)
    omdb_plot = fetch_omdb_plot(target_title)
    if omdb_plot:
        print(json.dumps({"plot": omdb_plot, "source": "omdb_en"}, ensure_ascii=False, indent=2))
        sys.exit(0)
    
    # Try Italian Wikipedia
    plot_it = fetch_wikipedia_plot(target_title, lang="it")
    if plot_it:
        print(json.dumps({"plot": plot_it, "source": "wikipedia_it"}, ensure_ascii=False, indent=2))
        sys.exit(0)
        
    # Fallback to English Wikipedia
    plot_en = fetch_wikipedia_plot(target_title, lang="en")
    if plot_en:
        print(json.dumps({"plot": plot_en, "source": "wikipedia_en"}, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"error": "Plot not found"}, indent=2))
