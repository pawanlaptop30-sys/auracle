from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging

from services.database import get_db
from services.auth import get_current_user, get_spotify_service, get_valid_spotify_token
from services.spotify import SpotifyService
from services.groq_ai import generate_squad_roast
from services.scoring import compute_squad_awards
from routers.profile import build_user_profile
from models.user import User
from models.squad import Squad, generate_squad_code

router = APIRouter()
logger = logging.getLogger(__name__)


class CreateSquadRequest(BaseModel):
    name: str = "The Squad"


@router.post("/create")
async def create_squad(
    req:     CreateSquadRequest,
    user:    User = Depends(get_current_user),
    spotify: SpotifyService = Depends(get_spotify_service),
    db:      AsyncSession = Depends(get_db),
):
    # Build creator's profile
    profile = await build_user_profile(spotify, "short_term")

    member_data = {
        "user_id":          user.id,
        "display_name":     user.display_name,
        "avatar_url":       user.avatar_url,
        "public_slug":      user.public_slug,
        "top_artist_names": profile["top_artist_names"][:5],
        "top_track_names":  profile["top_track_names"][:5],
        "genres":           profile["genres"][:8],
        "mood":             profile["mood"],
        "personality_type": profile["personality_type"],
        "scores":           profile["scores"],
        "intervention":     profile["intervention"],
        "top_tracks":       profile["top_tracks"][:5],
        "top_artists":      profile["top_artists"][:5],
    }

    code  = generate_squad_code()
    squad = Squad(
        code       = code,
        name       = req.name[:50],
        creator_id = user.id,
        members    = [member_data],
        expires_at = datetime.utcnow() + timedelta(hours=24),
    )
    db.add(squad)
    await db.commit()

    return {
        "code":        code,
        "name":        squad.name,
        "join_url":    f"/squad/{code}",
        "member_count": 1,
        "max_members":  4,
    }


@router.post("/join/{code}")
async def join_squad(
    code:    str,
    user:    User = Depends(get_current_user),
    spotify: SpotifyService = Depends(get_spotify_service),
    db:      AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Squad).where(Squad.code == code))
    squad  = result.scalar_one_or_none()
    if not squad:
        raise HTTPException(status_code=404, detail="Squad not found")
    if squad.is_complete:
        raise HTTPException(status_code=400, detail="Squad is already complete")
    if squad.expires_at and datetime.utcnow() > squad.expires_at:
        raise HTTPException(status_code=400, detail="Squad link has expired")

    members = squad.members or []

    # Check already joined
    if any(m["user_id"] == user.id for m in members):
        return {"code": code, "name": squad.name, "member_count": len(members), "already_joined": True}

    if len(members) >= squad.max_members:
        raise HTTPException(status_code=400, detail="Squad is full (max 4 members)")

    profile     = await build_user_profile(spotify, "short_term")
    member_data = {
        "user_id":          user.id,
        "display_name":     user.display_name,
        "avatar_url":       user.avatar_url,
        "public_slug":      user.public_slug,
        "top_artist_names": profile["top_artist_names"][:5],
        "top_track_names":  profile["top_track_names"][:5],
        "genres":           profile["genres"][:8],
        "mood":             profile["mood"],
        "personality_type": profile["personality_type"],
        "scores":           profile["scores"],
        "intervention":     profile["intervention"],
        "top_tracks":       profile["top_tracks"][:5],
        "top_artists":      profile["top_artists"][:5],
    }

    members.append(member_data)
    squad.members = members

    # Auto-compute results when 2+ members
    if len(members) >= 2:
        awards      = compute_squad_awards(members)
        group_roast = await generate_squad_roast(members)
        squad.awards      = awards
        squad.group_roast = group_roast
        squad.results     = _compute_results(members)

    if len(members) >= squad.max_members:
        squad.is_complete = True

    await db.commit()

    return {
        "code":         code,
        "name":         squad.name,
        "member_count": len(members),
        "is_complete":  squad.is_complete,
    }


def _compute_results(members: list) -> list:
    """Sort members by taste score for leaderboard."""
    return sorted(
        [{"display_name": m["display_name"], "avatar_url": m["avatar_url"],
          "personality_type": m["personality_type"], "score": m["scores"]["overall"],
          "top_artist": m["top_artist_names"][0] if m["top_artist_names"] else "???",
          "genres": m["genres"][:3]}
         for m in members],
        key=lambda x: x["score"],
        reverse=True,
    )


@router.get("/{code}")
async def get_squad(code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Squad).where(Squad.code == code))
    squad  = result.scalar_one_or_none()
    if not squad:
        raise HTTPException(status_code=404, detail="Squad not found")

    members = squad.members or []

    # Compute pairwise compatibility
    pairs = []
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            a, b = members[i], members[j]
            shared = list(
                set(a.get("top_artist_names", [])[:20]) &
                set(b.get("top_artist_names", [])[:20])
            )
            genre_shared = list(
                set(a.get("genres", [])[:10]) &
                set(b.get("genres", [])[:10])
            )
            artist_pct = len(shared) / 20 * 100
            genre_pct  = len(genre_shared) / max(
                len(set(a.get("genres", [])[:10]) | set(b.get("genres", [])[:10])), 1
            ) * 100
            pairs.append({
                "user_a":        a["display_name"],
                "user_b":        b["display_name"],
                "compat":        round(artist_pct * 0.6 + genre_pct * 0.4, 1),
                "shared_artists": shared[:5],
            })

    return {
        "code":         squad.code,
        "name":         squad.name,
        "member_count": len(members),
        "max_members":  squad.max_members,
        "is_complete":  squad.is_complete,
        "members":      [
            {
                "display_name":     m["display_name"],
                "avatar_url":       m["avatar_url"],
                "personality_type": m["personality_type"],
                "top_artist":       m["top_artist_names"][0] if m["top_artist_names"] else "???",
                "genres":           m["genres"][:3],
                "scores":           m["scores"],
                "mood":             m["mood"],
                "top_tracks":       m.get("top_tracks", [])[:5],
                "top_artists":      m.get("top_artists", [])[:5],
            }
            for m in members
        ],
        "leaderboard":  squad.results or _compute_results(members),
        "awards":       squad.awards or [],
        "group_roast":  squad.group_roast or "",
        "pairs":        pairs,
    }


@router.post("/{code}/refresh-roast")
async def refresh_roast(code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Squad).where(Squad.code == code))
    squad  = result.scalar_one_or_none()
    if not squad or not squad.members or len(squad.members) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 members to roast")
    roast         = await generate_squad_roast(squad.members)
    squad.group_roast = roast
    await db.commit()
    return {"group_roast": roast}
