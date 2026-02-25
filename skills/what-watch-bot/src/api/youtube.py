import requests
from src.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Native-language word for "trailer" per BCP-47 language prefix.
# YouTube ranking favors native-language terms for relevanceLanguage queries.
_TRAILER_KEYWORD = {
    'it': 'trailer ufficiale',
    'es': 'tráiler oficial',
    'fr': 'bande-annonce officielle',
    'de': 'offizieller Trailer',
    'pt': 'trailer oficial',
    'ja': '公式トレーラー',
    'ko': '공식 트레일러',
    'zh': '官方预告片',
}

def get_youtube_trailer(query, language='en-US', region='US'):
    if not Config.YOUTUBE_API_KEY:
        logger.warning("YouTube API key missing. Skipping trailer search.")
        return None

    # Extract 2-letter language code (e.g. 'it' from 'it-IT')
    lang_code = language.split('-')[0].lower()
    trailer_word = _TRAILER_KEYWORD.get(lang_code, 'official trailer')

    url = "https://www.googleapis.com/youtube/v3/search"
    search_query = f"{query} {trailer_word}"
    params = {
        'key': Config.YOUTUBE_API_KEY,
        'q': search_query,
        'part': 'snippet',
        'type': 'video',
        'maxResults': 1,
        'relevanceLanguage': lang_code,
        'regionCode': region,
    }
    try:
        logger.info(f"Searching YouTube for trailer: '{search_query}' (lang: {lang_code}, region: {region})")
        response = requests.get(url, params=params)
        if response.status_code == 200:
            items = response.json().get('items', [])
            if items:
                video_id = items[0]['id']['videoId']
                logger.info(f"Found YouTube trailer for '{query}': {video_id}")
                return f"https://www.youtube.com/watch?v={video_id}"
            else:
                logger.info(f"No YouTube trailer found for '{query}'")
        else:
            logger.warning(f"YouTube search failed for '{query}': status {response.status_code}")
    except Exception as e:
        logger.error(f"Error searching YouTube trailer for '{query}': {e}")
    return None
