import requests
from src.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)

def fetch_wikipedia_plot(title, lang="en"):
    """
    Search Wikipedia for the given title and return the extract (plot/overview).
    The 'lang' parameter is a Wikipedia language code (e.g., 'en', 'it', 'fr').
    """
    search_url = f"https://{lang}.wikipedia.org/w/api.php"
    contact = Config.CONTACT_URL or "https://github.com/your-username"
    headers = {"User-Agent": f"WhatWatchBot/1.0 ({contact})"}

    # Step 1: Search for the closest page title
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": f'intitle:"{title}"',
        "format": "json"
    }

    try:
        logger.info(f"Searching Wikipedia [{lang}] for title: '{title}'")
        response = requests.get(search_url, params=search_params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        search_results = data.get("query", {}).get("search", [])

        if not search_results:
            logger.info(f"Strict Wikipedia search failed. Trying broad search for '{title}'")
            # Try again less strictly
            search_params["srsearch"] = title
            response = requests.get(search_url, params=search_params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            search_results = data.get("query", {}).get("search", [])

        if not search_results:
            logger.warning(f"No Wikipedia [{lang}] results found for '{title}'")
            return None

        best_title = search_results[0]["title"]
        logger.info(f"Identified best Wikipedia article: '{best_title}'")

        # Step 2: Get the extract for the best title
        extract_params = {
            "action": "query",
            "prop": "extracts",
            "exintro": "true",
            "explaintext": "true",
            "titles": best_title,
            "format": "json"
        }

        logger.info(f"Fetching extract for Wikipedia article: '{best_title}'")
        response = requests.get(search_url, params=extract_params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        for page_id, page_info in pages.items():
            if "extract" in page_info:
                logger.info(f"Successfully fetched plot from Wikipedia [{lang}] for '{title}'")
                return page_info["extract"].strip()
                
        logger.warning(f"No extract present in Wikipedia article '{best_title}'")

    except Exception as e:
        logger.error(f"Error fetching Wikipedia plot for '{title}' [{lang}]: {e}")
        return None

    return None
