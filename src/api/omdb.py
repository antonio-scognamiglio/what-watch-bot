import requests
from src.config import Config

def get_omdb_ratings(title, year=None):
    if not Config.OMDB_API_KEY:
        return {}
    url = "http://www.omdbapi.com/"
    params = {'apikey': Config.OMDB_API_KEY, 't': title}
    if year:
        params['y'] = year
    try:
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
                return ratings
    except Exception:
        pass
    return {}

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
