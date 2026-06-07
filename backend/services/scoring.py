from typing import Dict, List
from collections import Counter

class ScoringService:
    def __init__(self):
        self.genre_weights = self._get_genre_weights()
    
    def _get_genre_weights(self) -> Dict[str, float]:
        """Define weights for different genres - these are used for scoring, not hardcoded genres"""
        return {
            'danceability': 0.15,
            'energy': 0.15,
            'valence': 0.10,
            'acousticness': 0.10,
            'instrumentalness': 0.10,
            'tempo': 0.05,
            'genre_diversity': 0.20,
            'artist_popularity': 0.15
        }
    
    def calculate_music_score(self, listening_data: Dict) -> Dict:
        """Calculate overall music taste score based on actual listening data"""
        audio_features = listening_data.get('audio_features', {})
        genres = listening_data.get('top_genres', {})
        
        score_breakdown = {}
        
        # Score based on actual audio features
        if audio_features:
            score_breakdown['danceability'] = audio_features.get('danceability', 0) * 100
            score_breakdown['energy'] = audio_features.get('energy', 0) * 100
            score_breakdown['valence'] = audio_features.get('valence', 0) * 100
            score_breakdown['acousticness'] = audio_features.get('acousticness', 0) * 100
            score_breakdown['instrumentalness'] = (1 - audio_features.get('instrumentalness', 0)) * 100
            score_breakdown['tempo_score'] = self._normalize_tempo(audio_features.get('tempo', 0))
        
        # Score based on genre diversity
        if genres:
            genre_count = len(genres)
            score_breakdown['genre_diversity'] = min(genre_count * 5, 100)
            
            # Get top genre score
            top_genre = list(genres.keys())[0] if genres else None
            top_genre_count = list(genres.values())[0] if genres else 0
            score_breakdown['genre_specialization'] = min(top_genre_count * 2, 100)
        
        # Calculate weighted total
        total_score = 0
        for key, weight in self.genre_weights.items():
            if key in score_breakdown:
                total_score += score_breakdown[key] * weight
        
        return {
            'total_score': round(total_score, 2),
            'breakdown': score_breakdown,
            'top_genres': dict(list(genres.items())[:5]) if genres else {},
            'listening_mood': self._determine_mood(audio_features) if audio_features else "Unknown"
        }
    
    def _normalize_tempo(self, tempo: float) -> float:
        """Normalize tempo to 0-100 scale"""
        # Typical tempo range: 60-200 BPM
        normalized = ((tempo - 60) / (200 - 60)) * 100
        return max(0, min(100, normalized))
    
    def _determine_mood(self, audio_features: Dict) -> str:
        """Determine listening mood based on actual audio features"""
        valence = audio_features.get('valence', 0)
        energy = audio_features.get('energy', 0)
        
        if valence > 0.6 and energy > 0.7:
            return "Energetic & Happy"
        elif valence > 0.6 and energy < 0.4:
            return "Chill & Happy"
        elif valence < 0.4 and energy > 0.7:
            return "Intense & Emotional"
        elif valence < 0.4 and energy < 0.4:
            return "Melancholic & Calm"
        elif energy > 0.7:
            return "High Energy"
        elif valence > 0.6:
            return "Positive Vibes"
        else:
            return "Balanced"
    
    def compare_users(self, user1_data: Dict, user2_data: Dict) -> Dict:
        """Compare music tastes between two users based on actual data"""
        user1_genres = set(user1_data.get('top_genres', {}).keys())
        user2_genres = set(user2_data.get('top_genres', {}).keys())
        
        common_genres = user1_genres.intersection(user2_genres)
        all_genres = user1_genres.union(user2_genres)
        
        similarity_score = len(common_genres) / len(all_genres) if all_genres else 0
        
        return {
            'similarity_score': round(similarity_score * 100, 2),
            'common_genres': list(common_genres),
            'user1_unique_genres': list(user1_genres - user2_genres),
            'user2_unique_genres': list(user2_genres - user1_genres),
            'compatibility': self._get_compatibility_level(similarity_score)
        }
    
    def _get_compatibility_level(self, score: float) -> str:
        """Get compatibility description"""
        if score > 0.7:
            return "Excellent Match!"
        elif score > 0.5:
            return "Great Match"
        elif score > 0.3:
            return "Good Match"
        elif score > 0.1:
            return "Somewhat Compatible"
        else:
            return "Different Tastes"

# Singleton instance
scoring_service = ScoringService()