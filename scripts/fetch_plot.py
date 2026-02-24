import os
import sys
import json
import requests
from config import Config

def fetch_omdb_plot(title):
    """
    Search OMDb for the exact movie/series plot (always in English, but reliable).
    """
    if not Config.OMDB_API_KEY:
        return None
        
    url = "http://www.omdbapi.com/"
    params = {'apikey': Config.OMDB_API_KEY, 't': title, 'plot': 'full'}
    
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            plot = data.get('Plot')
            if data.get('Response') == 'True' and plot and plot != 'N/A':
                return plot.strip()
    except Exception:
        pass
    return None

def fetch_wikipedia_plot(title, lang="it"):
    """
    Fallback: Search Wikipedia for the given title and return the extract (plot/overview).
    """
    search_url = f"https://{lang}.wikipedia.org/w/api.php"
    headers = {"User-Agent": "WhatWatchBot/1.0 (https://github.com/antonio-scognamiglio)"}
    
    # Step 1: Search for the closest page title
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": f'intitle:"{title}"',
        "format": "json"
    }
    
    try:
        response = requests.get(search_url, params=search_params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        search_results = data.get("query", {}).get("search", [])
        
        if not search_results:
            # Try again less strictly
            search_params["srsearch"] = title
            response = requests.get(search_url, params=search_params, headers=headers, timeout=5)
            data = response.json()
            search_results = data.get("query", {}).get("search", [])
            
        if not search_results:
            return None
            
        best_title = search_results[0]["title"]
        
        # Step 2: Get the extract for the best title
        extract_params = {
            "action": "query",
            "prop": "extracts",
            "exintro": "true",
            "explaintext": "true",
            "titles": best_title,
            "format": "json"
        }
        
        response = requests.get(search_url, params=extract_params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_info in pages.items():
            if "extract" in page_info:
                return page_info["extract"].strip()
                
    except Exception as e:
        return None
        
    return None

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
