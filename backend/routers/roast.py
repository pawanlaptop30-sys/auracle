from fastapi import APIRouter, Depends, HTTPException
from backend.services.spotify import SpotifyService
from backend.services.groq_ai import GroqAIService
from backend.services.auth import get_current_user
from typing import Dict

router = APIRouter(prefix="/roast", tags=["roast"])
spotify_service = SpotifyService()
groq_ai = GroqAIService()

@router.post("/me")
async def roast_me(current_user: Dict = Depends(get_current_user)):
    """Roast user based on their actual Spotify listening data"""
    try:
        access_token = current_user.get('spotify_access_token')
        if not access_token:
            raise HTTPException(status_code=401, detail="Spotify not connected")
        
        # Get actual listening data
        listening_data = spotify_service.analyze_listening_patterns(access_token)
        
        # Generate roast based on actual data
        roast = await groq_ai.generate_roast({
            'top_genres': listening_data.get('top_genres', {}),
            'top_tracks': listening_data.get('top_tracks', []),
            'top_artists': listening_data.get('top_artists', []),
            'audio_features': listening_data.get('audio_features', {})
        })
        
        return {
            'roast': roast,
            'based_on_data': {
                'genres_analyzed': len(listening_data.get('top_genres', {})),
                'tracks_analyzed': len(listening_data.get('top_tracks', [])),
                'artists_analyzed': len(listening_data.get('top_artists', []))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))