from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from urllib.parse import urlencode
import httpx, secrets, logging

from services.database import get_db
from services.auth import create_jwt, get_current_user
from services.spotify import SPOTIFY_AUTH_URL, SPOTIFY_TOKEN_URL, SPOTIFY_SCOPES, SpotifyService
from models.user import User, UserToken, generate_slug
from config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/login")
async def login():
    params = urlencode({
        "response_type": "code",
        "client_id":     settings.SPOTIFY_CLIENT_ID,
        "scope":         " ".join(SPOTIFY_SCOPES),
        "redirect_uri":  settings.SPOTIFY_REDIRECT_URI,
        "state":         secrets.token_urlsafe(16),
    })
    return RedirectResponse(f"{SPOTIFY_AUTH_URL}?{params}")


@router.get("/callback")
async def callback(
    code:  str = Query(None),
    error: str = Query(None),
    db:    AsyncSession = Depends(get_db),
):
    if error or not code:
        return RedirectResponse(f"{settings.FRONTEND_URL}/?error={error or 'no_code'}")

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                SPOTIFY_TOKEN_URL,
                data={
                    "grant_type":    "authorization_code",
                    "code":          code,
                    "redirect_uri":  settings.SPOTIFY_REDIRECT_URI,
                    "client_id":     settings.SPOTIFY_CLIENT_ID,
                    "client_secret": settings.SPOTIFY_CLIENT_SECRET,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if resp.status_code != 200:
                logger.error(f"Token exchange failed: {resp.text}")
                return RedirectResponse(f"{settings.FRONTEND_URL}/?error=token_failed")
            td = resp.json()
    except Exception as e:
        logger.error(f"Token exchange error: {e}")
        return RedirectResponse(f"{settings.FRONTEND_URL}/?error=token_error")

    access_token  = td.get("access_token")
    refresh_token = td.get("refresh_token", "")
    expires_in    = td.get("expires_in", 3600)

    try:
        spotify = SpotifyService(access_token)
        profile = await spotify.get_me()
    except Exception as e:
        logger.error(f"Profile fetch failed: {e}")
        return RedirectResponse(f"{settings.FRONTEND_URL}/?error=profile_failed")

    spotify_id   = profile.get("id")
    display_name = profile.get("display_name") or spotify_id
    email        = profile.get("email")
    images       = profile.get("images") or []
    avatar_url   = images[0].get("url") if images else None

    try:
        result = await db.execute(select(User).where(User.spotify_id == spotify_id))
        user   = result.scalar_one_or_none()
        if not user:
            user = User(
                spotify_id   = spotify_id,
                display_name = display_name,
                email        = email,
                avatar_url   = avatar_url,
                public_slug  = generate_slug(display_name),
            )
            db.add(user)
            await db.flush()
        else:
            user.display_name = display_name
            user.avatar_url   = avatar_url

        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        result2    = await db.execute(select(UserToken).where(UserToken.user_id == user.id))
        token_row  = result2.scalar_one_or_none()
        if token_row:
            token_row.access_token  = access_token
            token_row.refresh_token = refresh_token or token_row.refresh_token
            token_row.expires_at    = expires_at
        else:
            db.add(UserToken(user_id=user.id, access_token=access_token,
                             refresh_token=refresh_token, expires_at=expires_at))
        await db.commit()
    except Exception as e:
        logger.error(f"DB error: {e}", exc_info=True)
        await db.rollback()
        return RedirectResponse(f"{settings.FRONTEND_URL}/?error=db_error")

    token = create_jwt(user.id)
    return RedirectResponse(f"{settings.FRONTEND_URL}/auth/success?token={token}")


@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return {
        "id":           user.id,
        "display_name": user.display_name,
        "email":        user.email,
        "avatar_url":   user.avatar_url,
        "public_slug":  user.public_slug,
    }


@router.delete("/logout")
async def logout(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserToken).where(UserToken.user_id == user.id))
    t = result.scalar_one_or_none()
    if t:
        await db.delete(t)
        await db.commit()
    return {"message": "Logged out"}
