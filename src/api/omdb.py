import requests
from src.config import Config
from src.logger import get_logger

logger = get_logger(__name__)

def get_omdb_ratings(title, year=None):
    if not Config.OMDB_API_KEY:
        logger.warning("OMDB API key is missing. Skipping rating lookup.")
        return {}
    url = "http://www.omdbapi.com/"
    params = {'apikey': Config.OMDB_API_KEY, 't': title}
    if year:
        params['y'] = year
    try:
        logger.info(f"Fetching OMDb ratings for '{title}' (year={year})")
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('Response') == 'True':
                ratings = {}
                for r in data.get('Ratings', []):
                    source = r['Source']
                    value = r['Value']
                    if 'Rotten Tomatoes' in source:
                        ratings['tomatometer'] = int(value.replace('%', ''))
                    elif 'Internet Movie Database' in source:
                        ratings['imdb'] = float(value.split('/')[0])
                    elif 'Metacritic' in source:
                        ratings['metacritic'] = int(value.split('/')[0])
                logger.info(f"Loaded OMDB ratings for '{title}': {ratings}")
                return ratings
            else:
                logger.warning(f"OMDb returned errors for '{title}': {data.get('Error')}")
        else:
            logger.warning(f"OMDb rating fetch failed for '{title}': status {response.status_code}")
    except Exception as e:
        logger.error(f"Error searching OMDB ratings for '{title}': {e}")
    return {}

def fetch_omdb_plot(title):
    """
    Search OMDb for the exact movie/series plot (always in English, but reliable).
    """
    if not Config.OMDB_API_KEY:
        logger.warning("OMDB API key is missing. Skipping plot lookup.")
        return None
        
    url = "http://www.omdbapi.com/"
    params = {'apikey': Config.OMDB_API_KEY, 't': title, 'plot': 'full'}
    
    try:
        logger.info(f"Fetching OMDb full plot for '{title}'")
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            plot = data.get('Plot')
            if data.get('Response') == 'True' and plot and plot != 'N/A':
                logger.info(f"Found OMDb plot for '{title}'")
                return plot.strip()
            else:
                logger.warning(f"OMDb plot not found or empty for '{title}'")
        else:
            logger.warning(f"OMDb plot fetch failed for '{title}': status {response.status_code}")
    except Exception as e:
        logger.error(f"Error fetching OMDb plot for '{title}': {e}")
    return None
