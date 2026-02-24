import requests
from src.config import Config

def get_youtube_trailer(query):
    if not Config.YOUTUBE_API_KEY:
        return None
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'key': Config.YOUTUBE_API_KEY,
        'q': f"{query} trailer ufficiale",
        'part': 'snippet',
        'type': 'video',
        'maxResults': 1
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
