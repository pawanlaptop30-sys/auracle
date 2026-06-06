import httpx
import hashlib
import logging

logger = logging.getLogger(__name__)

SPOTIFY_API_BASE = "https://api.spotify.com/v1"
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

SPOTIFY_SCOPES = [
    "user-top-read",
    "user-read-recently-played",
    "user-read-email",
    "user-read-private",
    "playlist-read-private",
]


class SpotifyService:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {access_token}"}
        self._token_hash = hashlib.md5(access_token.encode()).hexdigest()[:12]

    async def _get(self, endpoint: str, params: dict = None, cache_ttl: int = 0):
        from services.redis_client import cache_get, cache_set
        # Never cache personal /me/ endpoints
        use_cache = cache_ttl > 0 and not endpoint.startswith("/me/")
        if use_cache:
            key = f"sp:{self._token_hash}:{endpoint}:{sorted((params or {}).items())}"
            cached = await cache_get(key)
            if cached:
                return cached

        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                f"{SPOTIFY_API_BASE}{endpoint}",
                headers=self.headers,
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()

        if use_cache:
            key = f"sp:{self._token_hash}:{endpoint}:{sorted((params or {}).items())}"
            await cache_set(key, data, cache_ttl)
        return data

    async def get_me(self):
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(f"{SPOTIFY_API_BASE}/me", headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def get_top_tracks(self, term: str = "short_term", limit: int = 50):
        return await self._get("/me/top/tracks", {"time_range": term, "limit": limit})

    async def get_top_artists(self, term: str = "short_term", limit: int = 50):
        return await self._get("/me/top/artists", {"time_range": term, "limit": limit})

    async def get_recently_played(self, limit: int = 50):
        return await self._get("/me/player/recently-played", {"limit": limit})

    async def get_artist(self, artist_id: str):
        return await self._get(f"/artists/{artist_id}", cache_ttl=3600)


async def refresh_access_token(refresh_token: str, client_id: str, client_secret: str) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            SPOTIFY_TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": client_id,
                "client_secret": client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
        return resp.json()
