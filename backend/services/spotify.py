from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from collections import Counter
from typing import Dict, List, Optional
import os

class SpotifyService:
    def __init__(self):
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
        self.sp = None
        
    def initialize(self):
        """Initialize Spotify client"""
        if not self.sp:
            self.sp = Spotify(auth_manager=SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope="user-top-read",
                show_dialog=True
            ))
        return self.sp
    
    def get_user_top_artists(self, access_token: str, time_range: str = 'medium_term', limit: int = 50) -> List[Dict]:
        """Get user's top artists"""
        sp = Spotify(auth=access_token)
        results = sp.current_user_top_artists(limit=limit, time_range=time_range)
        return results['items']
    
    def get_user_top_tracks(self, access_token: str, time_range: str = 'medium_term', limit: int = 50) -> List[Dict]:
        """Get user's top tracks"""
        sp = Spotify(auth=access_token)
        results = sp.current_user_top_tracks(limit=limit, time_range=time_range)
        return results['items']
    
    def get_user_profile(self, access_token: str) -> Dict:
        """Get user's Spotify profile"""
        sp = Spotify(auth=access_token)
        return sp.current_user()
    
    def get_artist_genres(self, access_token: str, artist_id: str) -> List[str]:
        """Get genres for a specific artist"""
        sp = Spotify(auth=access_token)
        artist = sp.artist(artist_id)
        return artist.get('genres', [])
    
    def get_user_genres_from_artists(self, access_token: str, time_range: str = 'medium_term', limit: int = 50) -> Dict[str, int]:
        """Get user's actual genres from their top artists"""
        top_artists = self.get_user_top_artists(access_token, time_range, limit)
        
        genre_counter = Counter()
        for artist in top_artists:
            artist_id = artist['id']
            genres = self.get_artist_genres(access_token, artist_id)
            for genre in genres:
                genre_counter[genre] += 1
        
        return dict(genre_counter.most_common())
    
    def get_audio_features_for_tracks(self, access_token: str, track_ids: List[str]) -> List[Dict]:
        """Get audio features for tracks"""
        sp = Spotify(auth=access_token)
        features = sp.audio_features(track_ids)
        return [f for f in features if f is not None]
    
    def analyze_listening_patterns(self, access_token: str, time_range: str = 'medium_term') -> Dict:
        """Comprehensive analysis of user's listening patterns"""
        sp = Spotify(auth=access_token)
        
        # Get top tracks
        top_tracks = sp.current_user_top_tracks(limit=50, time_range=time_range)
        tracks = top_tracks['items']
        
        # Get audio features
        track_ids = [track['id'] for track in tracks]
        audio_features = self.get_audio_features_for_tracks(access_token, track_ids)
        
        # Calculate averages
        if audio_features:
            avg_features = {
                'danceability': sum(f['danceability'] for f in audio_features) / len(audio_features),
                'energy': sum(f['energy'] for f in audio_features) / len(audio_features),
                'valence': sum(f['valence'] for f in audio_features) / len(audio_features),
                'acousticness': sum(f['acousticness'] for f in audio_features) / len(audio_features),
                'instrumentalness': sum(f['instrumentalness'] for f in audio_features) / len(audio_features),
                'tempo': sum(f['tempo'] for f in audio_features) / len(audio_features)
            }
        else:
            avg_features = {}
        
        # Get genres from all artists
        all_genres = Counter()
        all_artists = set()
        
        for track in tracks:
            for artist in track['artists']:
                artist_id = artist['id']
                if artist_id not in all_artists:
                    all_artists.add(artist_id)
                    genres = self.get_artist_genres(access_token, artist_id)
                    for genre in genres:
                        all_genres[genre] += 1
        
        # Get top artists
        top_artists = sp.current_user_top_artists(limit=10, time_range=time_range)
        
        return {
            'top_genres': dict(all_genres.most_common(20)),
            'audio_features': avg_features,
            'top_tracks': [
                {
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album': track['album']['name'],
                    'image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'preview_url': track['preview_url']
                }
                for track in tracks[:10]
            ],
            'top_artists': [
                {
                    'name': artist['name'],
                    'image': artist['images'][0]['url'] if artist['images'] else None,
                    'genres': self.get_artist_genres(access_token, artist['id']),
                    'popularity': artist['popularity']
                }
                for artist in top_artists['items'][:10]
            ]
        }