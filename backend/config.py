from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str
    SPOTIFY_REDIRECT_URI: str = "http://localhost:8000/auth/callback"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24 * 7

    SUPABASE_DB_URL: str = ""
    DATABASE_URL: str = ""

    REDIS_URL: str = "redis://localhost:6379"
    GROQ_API_KEY: str

    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:5173"
    ALLOWED_ORIGINS: str = ""
    ENV: str = "development"

    @property
    def db_url(self) -> str:
        url = self.SUPABASE_DB_URL or self.DATABASE_URL
        if not url:
            raise ValueError("Set SUPABASE_DB_URL in .env")
        for prefix in ("postgresql://", "postgres://"):
            if url.startswith(prefix) and "+asyncpg" not in url:
                url = url.replace(prefix, "postgresql+asyncpg://", 1)
                break
        return url

    @property
    def cors_origins(self) -> List[str]:
        origins: set = set()
        if self.FRONTEND_URL:
            origins.add(self.FRONTEND_URL.rstrip("/"))
        for port in [5173, 3000, 4173, 8080]:
            origins.add(f"http://localhost:{port}")
            origins.add(f"http://127.0.0.1:{port}")
        if self.ALLOWED_ORIGINS:
            for o in self.ALLOWED_ORIGINS.split(","):
                o = o.strip().rstrip("/")
                if o:
                    origins.add(o)
        return list(origins)

    class Config:
        env_file = ["../.env", ".env"]
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
