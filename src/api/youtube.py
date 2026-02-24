import requests
from src.config import Config

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
        return None

    # Extract 2-letter language code (e.g. 'it' from 'it-IT')
    lang_code = language.split('-')[0].lower()
    trailer_word = _TRAILER_KEYWORD.get(lang_code, 'official trailer')

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'key': Config.YOUTUBE_API_KEY,
        'q': f"{query} {trailer_word}",
        'part': 'snippet',
        'type': 'video',
        'maxResults': 1,
        'relevanceLanguage': lang_code,
        'regionCode': region,
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            items = response.json().get('items', [])
            if items:
                video_id = items[0]['id']['videoId']
                return f"https://www.youtube.com/watch?v={video_id}"
    except Exception:
        pass
    return None
