from fastapi import APIRouter, Depends, HTTPException
from backend.services.spotify import SpotifyService
from backend.services.scoring import scoring_service
from backend.services.auth import get_current_user
from backend.models.squad import SquadRoom
from typing import Dict

router = APIRouter(prefix="/battle", tags=["battle"])
spotify_service = SpotifyService()

@router.post("/start/{room_id}")
async def start_battle(
    room_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Start a music battle based on actual listening data"""
    try:
        access_token = current_user.get('spotify_access_token')
        if not access_token:
            raise HTTPException(status_code=401, detail="Spotify not connected")
        
        # Get room participants
        room = await SquadRoom.get(room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        # Get actual data for all participants
        participants_data = {}
        for user_id in room.participants:
            # Get each user's actual listening data
            user_data = spotify_service.analyze_listening_patterns(
                room.get_user_token(user_id)
            )
            participants_data[user_id] = user_data
        
        # Compare users based on actual data
        comparisons = {}
        user_ids = list(participants_data.keys())
        for i in range(len(user_ids)):
            for j in range(i+1, len(user_ids)):
                comparison = scoring_service.compare_users(
                    participants_data[user_ids[i]],
                    participants_data[user_ids[j]]
                )
                comparisons[f"{user_ids[i]}_vs_{user_ids[j]}"] = comparison
        
        return {
            'participants_count': len(participants_data),
            'comparisons': comparisons,
            'common_genres': self._find_common_genres(participants_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _find_common_genres(self, participants_data: Dict) -> list:
    """Find genres common among all participants"""
    genre_sets = []
    for user_data in participants_data.values():
        genres = set(user_data.get('top_genres', {}).keys())
        genre_sets.append(genres)
    
    if genre_sets:
        common = genre_sets[0]
        for genre_set in genre_sets[1:]:
            common = common.intersection(genre_set)
        return list(common)
    return []