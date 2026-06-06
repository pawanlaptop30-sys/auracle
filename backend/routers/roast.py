from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from services.auth import get_current_user, get_spotify_service
from services.spotify import SpotifyService
from routers.profile import build_user_profile
from services.groq_ai import (
    generate_roast, generate_category_roast,
    generate_alibi, generate_music_horoscope
)
from models.user import User
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

VALID_SEVERITIES  = {"gentle", "roasted", "destroyed", "courtroom"}
VALID_CATEGORIES  = {"age", "mainstream", "obsessive", "sad", "energy"}
VALID_TERMS       = {"short_term", "medium_term", "long_term"}


@router.get("/me")
async def roast_me(
    severity: str = Query("roasted"),
    term:     str = Query("short_term"),
    user:     User = Depends(get_current_user),
    spotify:  SpotifyService = Depends(get_spotify_service),
):
    if severity not in VALID_SEVERITIES:
        severity = "roasted"
    if term not in VALID_TERMS:
        term = "short_term"

    profile = await build_user_profile(spotify, term)

    user_data = {
        "name":             user.display_name,
        "top_artists":      profile["top_artist_names"][:6],
        "top_tracks":       profile["top_track_names"][:6],
        "genres":           profile["genres"][:5],
        "personality_type": profile["personality_type"],
        "energy":           profile["mood"].get("energy", 0.5),
        "valence":          profile["mood"].get("valence", 0.5),
    }

    roast_text = await generate_roast(user_data, severity)

    return {
        "severity":         severity,
        "roast":            roast_text,
        "personality_type": profile["personality_type"],
        "top_artist":       profile["top_artist_names"][0] if profile["top_artist_names"] else None,
        "scores":           profile["scores"],
    }


@router.get("/category")
async def roast_category(
    category: str = Query("mainstream"),
    term:     str = Query("short_term"),
    user:     User = Depends(get_current_user),
    spotify:  SpotifyService = Depends(get_spotify_service),
):
    if category not in VALID_CATEGORIES:
        category = "mainstream"
    if term not in VALID_TERMS:
        term = "short_term"

    profile = await build_user_profile(spotify, term)
    user_data = {
        "name":        user.display_name,
        "top_artists": profile["top_artist_names"][:5],
        "top_tracks":  profile["top_track_names"][:5],
        "genres":      profile["genres"][:4],
    }

    roast_text = await generate_category_roast(user_data, category)
    return {"category": category, "roast": roast_text}


@router.get("/alibi")
async def get_alibi(
    term:    str = Query("short_term"),
    user:    User = Depends(get_current_user),
    spotify: SpotifyService = Depends(get_spotify_service),
):
    if term not in VALID_TERMS:
        term = "short_term"
    profile = await build_user_profile(spotify, term)
    alibi   = await generate_alibi({
        "top_artists": profile["top_artist_names"][:4],
        "genres":      profile["genres"][:3],
    })
    return {"alibi": alibi}
