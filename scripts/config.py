import os
from dotenv import load_dotenv

# Load environment variables once for all scripts using Config
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)

class Config:
    TMDB_API_KEY = os.getenv('TMDB_API_KEY')
    OMDB_API_KEY = os.getenv('OMDB_API_KEY')
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    REGION = os.getenv('REGION', 'IT')
    LANGUAGE = os.getenv('LANGUAGE', 'it-IT')

GENRE_MAPPING = {
    28: 'Azione', 12: 'Avventura', 16: 'Animazione', 35: 'Commedia', 
    80: 'Crime', 99: 'Documentario', 18: 'Dramma', 10751: 'Famiglia', 
    14: 'Fantasy', 36: 'Storia', 27: 'Horror', 10402: 'Musica', 
    9648: 'Mistero', 10749: 'Romantico', 878: 'Fantascienza', 
    53: 'Thriller', 10752: 'Guerra', 37: 'Western',
    10759: 'Azione e Avventura', 10762: 'Kids', 10763: 'News', 
    10764: 'Reality', 10765: 'Sci-Fi e Fantasy', 10766: 'Soap', 
    10767: 'Talk', 10768: 'Guerra e Politica'
}
