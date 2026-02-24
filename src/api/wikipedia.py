import requests

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
