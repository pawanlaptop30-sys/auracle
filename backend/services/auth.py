from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config import settings
from services.database import get_db
from models.user import User, UserToken
from services.spotify import SpotifyService, refresh_access_token

security = HTTPBearer()


def create_jwt(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRE_HOURS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_jwt(credentials.credentials)
    result = await db.execute(select(User).where(User.id == int(payload["sub"])))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


async def get_valid_spotify_token(user: User, db: AsyncSession) -> str:
    result = await db.execute(select(UserToken).where(UserToken.user_id == user.id))
    token_row = result.scalar_one_or_none()
    if not token_row:
        raise HTTPException(status_code=401, detail="No Spotify token found")
    if datetime.utcnow() >= token_row.expires_at - timedelta(minutes=5):
        refreshed = await refresh_access_token(
            token_row.refresh_token,
            settings.SPOTIFY_CLIENT_ID,
            settings.SPOTIFY_CLIENT_SECRET,
        )
        token_row.access_token = refreshed["access_token"]
        token_row.expires_at = datetime.utcnow() + timedelta(seconds=refreshed["expires_in"])
        await db.commit()
    return token_row.access_token


async def get_spotify_service(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SpotifyService:
    token = await get_valid_spotify_token(user, db)
    return SpotifyService(token)
