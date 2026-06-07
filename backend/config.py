import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Spotify Configuration
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL")
    
    # Groq AI
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # JWT
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_ALGORITHM = "HS256"
    
    # Last.fm
    LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
    LASTFM_API_SECRET = os.getenv("LASTFM_API_SECRET")