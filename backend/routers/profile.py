from fastapi import APIRouter, Depends, HTTPException
from backend.services.spotify import SpotifyService
from backend.services.scoring import scoring_service
from backend.services.auth import get_current_user
from typing import Dict

router = APIRouter(prefix="/profile", tags=["profile"])
spotify_service = SpotifyService()

@router.get("/me")
async def get_my_profile(current_user: Dict = Depends(get_current_user)):
    """Get current user's profile with actual Spotify data"""
    try:
        access_token = current_user.get('spotify_access_token')
        if not access_token:
            raise HTTPException(status_code=401, detail="Spotify not connected")
        
        # Get actual Spotify profile
        spotify_profile = spotify_service.get_user_profile(access_token)
        
        # Get actual listening analysis
        listening_data = spotify_service.analyze_listening_patterns(access_token)
        
        # Calculate scores based on actual data
        music_score = scoring_service.calculate_music_score(listening_data)
        
        return {
            'spotify_profile': {
                'display_name': spotify_profile.get('display_name'),
                'followers': spotify_profile.get('followers', {}).get('total', 0),
                'image': spotify_profile.get('images', [{}])[0].get('url') if spotify_profile.get('images') else None,
                'country': spotify_profile.get('country'),
                'product': spotify_profile.get('product')
            },
            'listening_analysis': {
                'top_genres': listening_data.get('top_genres', {}),
                'audio_features': listening_data.get('audio_features', {}),
                'top_tracks': listening_data.get('top_tracks', []),
                'top_artists': listening_data.get('top_artists', [])
            },
            'music_score': music_score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/genres")
async def get_my_genres(
    time_range: str = 'medium_term',
    current_user: Dict = Depends(get_current_user)
):
    """Get user's actual Spotify genres"""
    try:
        access_token = current_user.get('spotify_access_token')
        if not access_token:
            raise HTTPException(status_code=401, detail="Spotify not connected")
        
        genres = spotify_service.get_user_genres_from_artists(access_token, time_range)
        
        return {
            'time_range': time_range,
            'genres': genres,
            'total_unique_genres': len(genres)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio-features")
async def get_audio_features(
    time_range: str = 'medium_term',
    current_user: Dict = Depends(get_current_user)
):
    """Get user's audio features from actual listening data"""
    try:
        access_token = current_user.get('spotify_access_token')
        if not access_token:
            raise HTTPException(status_code=401, detail="Spotify not connected")
        
        listening_data = spotify_service.analyze_listening_patterns(access_token, time_range)
        
        return {
            'time_range': time_range,
            'audio_features': listening_data.get('audio_features', {}),
            'derived_mood': scoring_service._determine_mood(listening_data.get('audio_features', {}))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))