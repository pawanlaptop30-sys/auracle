from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from services.database import get_db
from services.auth import get_current_user, get_spotify_service, get_valid_spotify_token
from services.spotify import SpotifyService
from services.scoring import (
    derive_mood_from_genres, get_personality_type,
    compute_taste_score, detect_intervention
)
from services.groq_ai import generate_music_horoscope, generate_taste_in_three_words
from models.user import User
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

VALID_TERMS = {"short_term", "medium_term", "long_term"}


async def build_user_profile(spotify: SpotifyService, term: str = "short_term") -> dict:
    """Build complete user profile from their own Spotify data only."""
    try:
        tracks_data  = await spotify.get_top_tracks(term, 50)
        tracks       = tracks_data.get("items", [])
    except Exception as e:
        logger.error(f"Tracks fetch failed: {e}")
        tracks = []

    try:
        artists_data = await spotify.get_top_artists(term, 50)
        artists      = artists_data.get("items", [])
    except Exception as e:
        logger.error(f"Artists fetch failed: {e}")
        artists = []

    # Extract genres from user's own top artists
    all_genres: list = []
    for a in artists:
        all_genres.extend(a.get("genres", []))

    # Unique genres sorted by frequency
    genre_counts: dict = {}
    for g in all_genres:
        genre_counts[g] = genre_counts.get(g, 0) + 1
    genres_sorted = sorted(genre_counts, key=genre_counts.get, reverse=True)

    # Derive mood from user's genres
    mood = derive_mood_from_genres(genres_sorted[:10])

    # Top artist names and track names
    top_artist_names = [a.get("name", "") for a in artists[:10]]
    top_track_names  = [t.get("name", "") for t in tracks[:10]]

    # Track data for scoring
    tracks_for_scoring = []
    for t in tracks:
        tracks_for_scoring.append({
            "name":    t.get("name", ""),
            "artists": [a.get("name", "") for a in t.get("artists", [])],
        })

    personality   = get_personality_type(mood, top_artist_names, genres_sorted)
    taste_scores  = compute_taste_score(mood, genres_sorted, top_artist_names, tracks_for_scoring)
    intervention  = detect_intervention(top_artist_names, tracks_for_scoring)

    # Format top tracks for response
    formatted_tracks = []
    for i, t in enumerate(tracks[:20]):
        try:
            album  = t.get("album") or {}
            images = album.get("images") or [{}]
            formatted_tracks.append({
                "rank":       i + 1,
                "id":         t.get("id", ""),
                "name":       t.get("name", "Unknown"),
                "artists":    [a.get("name", "") for a in t.get("artists", [])],
                "album":      album.get("name", ""),
                "album_art":  images[0].get("url") if images else None,
                "popularity": t.get("popularity", 0),
                "preview_url": t.get("preview_url"),
                "external_url": (t.get("external_urls") or {}).get("spotify", ""),
            })
        except Exception:
            continue

    # Format top artists for response
    formatted_artists = []
    for i, a in enumerate(artists[:20]):
        try:
            images = a.get("images") or [{}]
            formatted_artists.append({
                "rank":       i + 1,
                "id":         a.get("id", ""),
                "name":       a.get("name", "Unknown"),
                "genres":     a.get("genres", [])[:3],
                "popularity": a.get("popularity", 0),
                "followers":  (a.get("followers") or {}).get("total", 0),
                "image":      images[0].get("url") if images else None,
            })
        except Exception:
            continue

    return {
        "term":             term,
        "top_tracks":       formatted_tracks,
        "top_artists":      formatted_artists,
        "top_artist_names": top_artist_names,
        "top_track_names":  top_track_names,
        "genres":           genres_sorted[:15],
        "mood":             mood,
        "personality_type": personality,
        "scores":           taste_scores,
        "intervention":     intervention,
    }


@router.get("/me")
async def get_my_profile(
    term: str = Query("short_term"),
    user: User = Depends(get_current_user),
    spotify: SpotifyService = Depends(get_spotify_service),
):
    if term not in VALID_TERMS:
        term = "short_term"
    profile = await build_user_profile(spotify, term)
    return {
        "user": {
            "id":           user.id,
            "display_name": user.display_name,
            "avatar_url":   user.avatar_url,
            "public_slug":  user.public_slug,
        },
        **profile,
    }


@router.get("/me/horoscope")
async def get_horoscope(
    term: str = Query("short_term"),
    user: User = Depends(get_current_user),
    spotify: SpotifyService = Depends(get_spotify_service),
):
    if term not in VALID_TERMS:
        term = "short_term"
    profile = await build_user_profile(spotify, term)
    horoscope = await generate_music_horoscope({
        "name":             user.display_name,
        "top_artists":      profile["top_artist_names"][:4],
        "personality_type": profile["personality_type"],
        "energy":           profile["mood"].get("energy", 0.5),
    })
    three_words = await generate_taste_in_three_words({
        "top_artists": profile["top_artist_names"][:3],
        "genres":      profile["genres"][:3],
    })
    return {"horoscope": horoscope, "three_words": three_words}


@router.get("/{slug}")
async def get_public_profile(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Public profile — only returns non-sensitive display data."""
    result = await db.execute(select(User).where(User.public_slug == slug))
    user   = result.scalar_one_or_none()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Profile not found")
    return {
        "id":           user.id,
        "display_name": user.display_name,
        "avatar_url":   user.avatar_url,
        "public_slug":  user.public_slug,
        "member_since": user.created_at.isoformat(),
    }
