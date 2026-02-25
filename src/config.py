import os
from dotenv import load_dotenv

# Load environment variables once for all scripts using Config
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)

class Config:
    # Required API keys — must be set in .env
    TMDB_API_KEY = os.getenv('TMDB_API_KEY')
    OMDB_API_KEY = os.getenv('OMDB_API_KEY')
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    # Deployer contact URL (used in Wikipedia User-Agent header per Wikipedia policy)
    CONTACT_URL = os.getenv('CONTACT_URL', '')
    # Path for SQLite Database, defaults to local db/watchbot.db
    DB_PATH = os.getenv('DB_PATH', os.path.join(os.path.dirname(__file__), '..', 'db', 'watchbot.db'))

GENRE_MAPPING = {
    28: 'Action', 12: 'Adventure', 16: 'Animation', 35: 'Comedy',
    80: 'Crime', 99: 'Documentary', 18: 'Drama', 10751: 'Family',
    14: 'Fantasy', 36: 'History', 27: 'Horror', 10402: 'Music',
    9648: 'Mystery', 10749: 'Romance', 878: 'Science Fiction',
    53: 'Thriller', 10752: 'War', 37: 'Western',
    10759: 'Action & Adventure', 10762: 'Kids', 10763: 'News',
    10764: 'Reality', 10765: 'Sci-Fi & Fantasy', 10766: 'Soap',
    10767: 'Talk', 10768: 'War & Politics'
}
