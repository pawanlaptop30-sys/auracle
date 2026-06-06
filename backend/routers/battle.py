from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid, logging

from services.database import get_db
from services.auth import get_current_user, get_spotify_service, get_valid_spotify_token
from services.spotify import SpotifyService
from services.groq_ai import generate_battle_verdict, generate_compatibility_tagline
from routers.profile import build_user_profile
from models.user import User
from models.squad import Battle

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/create")
async def create_battle(
    target_slug: str = Query(...),
    term:        str = Query("short_term"),
    user:        User = Depends(get_current_user),
    spotify:     SpotifyService = Depends(get_spotify_service),
    db:          AsyncSession = Depends(get_db),
):
    # Find opponent
    result  = await db.execute(select(User).where(User.public_slug == target_slug))
    opponent = result.scalar_one_or_none()
    if not opponent:
        raise HTTPException(status_code=404, detail="Opponent not found")
    if opponent.id == user.id:
        raise HTTPException(status_code=400, detail="Cannot battle yourself")

    # Build both profiles
    profile_a = await build_user_profile(spotify, term)

    try:
        token_b   = await get_valid_spotify_token(opponent, db)
        spotify_b = SpotifyService(token_b)
        profile_b = await build_user_profile(spotify_b, term)
    except Exception as e:
        logger.error(f"Opponent profile failed: {e}")
        raise HTTPException(status_code=400, detail="Could not fetch opponent's Spotify data")

    user_a_data = {
        "name":             user.display_name,
        "avatar_url":       user.avatar_url,
        "public_slug":      user.public_slug,
        "top_artists":      profile_a["top_artist_names"][:5],
        "genres":           profile_a["genres"][:4],
        "personality_type": profile_a["personality_type"],
        "taste_score":      profile_a["scores"]["overall"],
        "mood":             profile_a["mood"],
        "top_tracks":       profile_a["top_track_names"][:5],
        "scores":           profile_a["scores"],
    }
    user_b_data = {
        "name":             opponent.display_name,
        "avatar_url":       opponent.avatar_url,
        "public_slug":      opponent.public_slug,
        "top_artists":      profile_b["top_artist_names"][:5],
        "genres":           profile_b["genres"][:4],
        "personality_type": profile_b["personality_type"],
        "taste_score":      profile_b["scores"]["overall"],
        "mood":             profile_b["mood"],
        "top_tracks":       profile_b["top_track_names"][:5],
        "scores":           profile_b["scores"],
    }

    # Compute shared artists
    shared_artists = list(
        set(profile_a["top_artist_names"][:20]) &
        set(profile_b["top_artist_names"][:20])
    )

    # Compatibility score
    artist_overlap = len(shared_artists) / 20 * 100
    genre_overlap  = len(
        set(profile_a["genres"][:10]) & set(profile_b["genres"][:10])
    ) / max(len(set(profile_a["genres"][:10]) | set(profile_b["genres"][:10])), 1) * 100

    import numpy as np
    keys  = ["energy", "valence", "dance", "mainstream"]
    vec_a = [profile_a["mood"].get(k, 0) for k in keys]
    vec_b = [profile_b["mood"].get(k, 0) for k in keys]
    na, nb = (sum(x**2 for x in vec_a)**0.5), (sum(x**2 for x in vec_b)**0.5)
    mood_sim = (sum(a*b for a,b in zip(vec_a,vec_b)) / (na*nb) * 100) if na and nb else 50

    compat_score = round(artist_overlap*0.40 + genre_overlap*0.30 + mood_sim*0.30, 1)

    # AI verdict
    verdict = await generate_battle_verdict(user_a_data, user_b_data)
    tagline = await generate_compatibility_tagline(user_a_data, user_b_data, compat_score)

    # Save battle
    slug    = str(uuid.uuid4())[:8]
    battle  = Battle(
        slug        = slug,
        user_a_id   = user.id,
        user_b_id   = opponent.id,
        user_a_data = user_a_data,
        user_b_data = user_b_data,
        verdict     = {**verdict, "tagline": tagline, "compat_score": compat_score, "shared_artists": shared_artists},
        winner_name = verdict.get("winner"),
    )
    db.add(battle)
    await db.commit()

    return {"slug": slug, "redirect": f"/battle/{slug}"}


@router.get("/{slug}")
async def get_battle(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Battle).where(Battle.slug == slug))
    battle = result.scalar_one_or_none()
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")
    return {
        "slug":       battle.slug,
        "user_a":     battle.user_a_data,
        "user_b":     battle.user_b_data,
        "verdict":    battle.verdict,
        "winner":     battle.winner_name,
        "created_at": battle.created_at.isoformat(),
    }
