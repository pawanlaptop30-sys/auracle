import httpx
import logging
from config import settings

logger = logging.getLogger(__name__)

LASTFM_BASE = "https://ws.audioscrobbler.com/2.0/"

# Last.fm tag → mood values
TAG_MOOD_MAP = {
    # Energy
    "energetic":     {"energy": 0.90, "valence": 0.65, "dance": 0.80, "mainstream": 0.60},
    "aggressive":    {"energy": 0.92, "valence": 0.35, "dance": 0.55, "mainstream": 0.40},
    "intense":       {"energy": 0.88, "valence": 0.45, "dance": 0.60, "mainstream": 0.50},
    "upbeat":        {"energy": 0.82, "valence": 0.78, "dance": 0.80, "mainstream": 0.70},
    "powerful":      {"energy": 0.85, "valence": 0.55, "dance": 0.60, "mainstream": 0.50},
    "fast":          {"energy": 0.85, "valence": 0.58, "dance": 0.72, "mainstream": 0.52},
    "loud":          {"energy": 0.88, "valence": 0.50, "dance": 0.60, "mainstream": 0.48},
    # Happy / Positive
    "happy":         {"energy": 0.72, "valence": 0.88, "dance": 0.75, "mainstream": 0.70},
    "feel good":     {"energy": 0.70, "valence": 0.85, "dance": 0.72, "mainstream": 0.72},
    "feelgood":      {"energy": 0.70, "valence": 0.85, "dance": 0.72, "mainstream": 0.72},
    "positive":      {"energy": 0.68, "valence": 0.82, "dance": 0.70, "mainstream": 0.65},
    "fun":           {"energy": 0.75, "valence": 0.85, "dance": 0.78, "mainstream": 0.72},
    "euphoric":      {"energy": 0.88, "valence": 0.90, "dance": 0.85, "mainstream": 0.65},
    "party":         {"energy": 0.85, "valence": 0.80, "dance": 0.88, "mainstream": 0.75},
    "cheerful":      {"energy": 0.72, "valence": 0.86, "dance": 0.74, "mainstream": 0.68},
    "joyful":        {"energy": 0.70, "valence": 0.88, "dance": 0.72, "mainstream": 0.65},
    # Sad / Dark
    "sad":           {"energy": 0.35, "valence": 0.22, "dance": 0.32, "mainstream": 0.55},
    "melancholic":   {"energy": 0.38, "valence": 0.28, "dance": 0.35, "mainstream": 0.45},
    "melancholy":    {"energy": 0.38, "valence": 0.28, "dance": 0.35, "mainstream": 0.45},
    "depressing":    {"energy": 0.30, "valence": 0.18, "dance": 0.28, "mainstream": 0.40},
    "dark":          {"energy": 0.62, "valence": 0.28, "dance": 0.48, "mainstream": 0.40},
    "emotional":     {"energy": 0.45, "valence": 0.35, "dance": 0.38, "mainstream": 0.55},
    "heartbreak":    {"energy": 0.42, "valence": 0.25, "dance": 0.35, "mainstream": 0.58},
    "heartbreaking": {"energy": 0.42, "valence": 0.25, "dance": 0.35, "mainstream": 0.55},
    "gloomy":        {"energy": 0.32, "valence": 0.22, "dance": 0.28, "mainstream": 0.40},
    "lonely":        {"energy": 0.30, "valence": 0.20, "dance": 0.25, "mainstream": 0.48},
    "cry":           {"energy": 0.35, "valence": 0.20, "dance": 0.28, "mainstream": 0.52},
    # Chill / Calm
    "chill":         {"energy": 0.32, "valence": 0.58, "dance": 0.45, "mainstream": 0.55},
    "chillout":      {"energy": 0.30, "valence": 0.58, "dance": 0.42, "mainstream": 0.50},
    "relaxing":      {"energy": 0.28, "valence": 0.60, "dance": 0.38, "mainstream": 0.48},
    "relax":         {"energy": 0.28, "valence": 0.60, "dance": 0.38, "mainstream": 0.48},
    "calm":          {"energy": 0.25, "valence": 0.55, "dance": 0.32, "mainstream": 0.42},
    "peaceful":      {"energy": 0.22, "valence": 0.62, "dance": 0.28, "mainstream": 0.38},
    "ambient":       {"energy": 0.20, "valence": 0.52, "dance": 0.25, "mainstream": 0.25},
    "sleep":         {"energy": 0.18, "valence": 0.50, "dance": 0.20, "mainstream": 0.35},
    "study":         {"energy": 0.30, "valence": 0.55, "dance": 0.35, "mainstream": 0.40},
    "mellow":        {"energy": 0.35, "valence": 0.55, "dance": 0.40, "mainstream": 0.48},
    "slow":          {"energy": 0.30, "valence": 0.52, "dance": 0.35, "mainstream": 0.50},
    # Dance
    "danceable":     {"energy": 0.78, "valence": 0.72, "dance": 0.92, "mainstream": 0.70},
    "dance":         {"energy": 0.80, "valence": 0.72, "dance": 0.90, "mainstream": 0.72},
    "groovy":        {"energy": 0.72, "valence": 0.75, "dance": 0.88, "mainstream": 0.62},
    "funky":         {"energy": 0.70, "valence": 0.72, "dance": 0.85, "mainstream": 0.58},
    "club":          {"energy": 0.85, "valence": 0.70, "dance": 0.90, "mainstream": 0.75},
    # Romantic
    "romantic":      {"energy": 0.48, "valence": 0.72, "dance": 0.55, "mainstream": 0.65},
    "love":          {"energy": 0.52, "valence": 0.75, "dance": 0.58, "mainstream": 0.68},
    "sexy":          {"energy": 0.65, "valence": 0.68, "dance": 0.75, "mainstream": 0.65},
    "sensual":       {"energy": 0.60, "valence": 0.65, "dance": 0.72, "mainstream": 0.60},
    # Motivational
    "motivational":  {"energy": 0.85, "valence": 0.75, "dance": 0.70, "mainstream": 0.65},
    "workout":       {"energy": 0.90, "valence": 0.65, "dance": 0.78, "mainstream": 0.62},
    "epic":          {"energy": 0.88, "valence": 0.60, "dance": 0.55, "mainstream": 0.52},
    "hype":          {"energy": 0.90, "valence": 0.70, "dance": 0.82, "mainstream": 0.68},
    # Mainstream
    "pop":           {"energy": 0.72, "valence": 0.70, "dance": 0.75, "mainstream": 0.92},
    "mainstream":    {"energy": 0.70, "valence": 0.68, "dance": 0.72, "mainstream": 0.95},
    "top 40":        {"energy": 0.72, "valence": 0.70, "dance": 0.75, "mainstream": 0.95},
    "popular":       {"energy": 0.70, "valence": 0.68, "dance": 0.72, "mainstream": 0.90},
    "chart":         {"energy": 0.70, "valence": 0.68, "dance": 0.72, "mainstream": 0.88},
    # Underground / Niche
    "underground":   {"energy": 0.68, "valence": 0.50, "dance": 0.60, "mainstream": 0.15},
    "indie":         {"energy": 0.58, "valence": 0.55, "dance": 0.55, "mainstream": 0.22},
    "obscure":       {"energy": 0.55, "valence": 0.48, "dance": 0.50, "mainstream": 0.10},
    "alternative":   {"energy": 0.65, "valence": 0.48, "dance": 0.55, "mainstream": 0.35},
    # Indian / Regional
    "bollywood":     {"energy": 0.72, "valence": 0.70, "dance": 0.74, "mainstream": 0.68},
    "filmi":         {"energy": 0.68, "valence": 0.66, "dance": 0.70, "mainstream": 0.65},
    "desi":          {"energy": 0.70, "valence": 0.68, "dance": 0.72, "mainstream": 0.62},
    "bhangra":       {"energy": 0.85, "valence": 0.78, "dance": 0.88, "mainstream": 0.55},
    "sufi":          {"energy": 0.42, "valence": 0.68, "dance": 0.45, "mainstream": 0.38},
    "devotional":    {"energy": 0.45, "valence": 0.72, "dance": 0.40, "mainstream": 0.32},
    "classical":     {"energy": 0.28, "valence": 0.58, "dance": 0.28, "mainstream": 0.28},
    "kollywood":     {"energy": 0.70, "valence": 0.68, "dance": 0.72, "mainstream": 0.55},
    "tollywood":     {"energy": 0.70, "valence": 0.68, "dance": 0.72, "mainstream": 0.52},
    "punjabi":       {"energy": 0.80, "valence": 0.72, "dance": 0.82, "mainstream": 0.60},
}


async def get_track_tags(artist: str, track: str) -> list[str]:
    """Fetch top tags for a track from Last.fm."""
    if not settings.LASTFM_API_KEY:
        return []
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(LASTFM_BASE, params={
                "method":  "track.getTopTags",
                "artist":  artist,
                "track":   track,
                "api_key": settings.LASTFM_API_KEY,
                "format":  "json",
            })
            if resp.status_code != 200:
                return []
            data = resp.json()
            tags = data.get("toptags", {}).get("tag", [])
            # Only reliable tags with count > 10
            return [
                t["name"].lower() for t in tags[:8]
                if int(t.get("count", 0)) > 10
            ]
    except Exception as e:
        logger.warning(f"Last.fm tag fetch failed for {artist} - {track}: {e}")
        return []


def tags_to_mood(tags: list[str]) -> dict | None:
    """Convert Last.fm tags to mood values."""
    if not tags:
        return None

    energy_vals, valence_vals, dance_vals, mainstream_vals = [], [], [], []

    for tag in tags:
        for key, mood in TAG_MOOD_MAP.items():
            if key in tag or tag in key:
                energy_vals.append(mood["energy"])
                valence_vals.append(mood["valence"])
                dance_vals.append(mood["dance"])
                mainstream_vals.append(mood["mainstream"])
                break

    if not energy_vals:
        return None

    return {
        "energy":     round(sum(energy_vals)     / len(energy_vals),     3),
        "valence":    round(sum(valence_vals)     / len(valence_vals),    3),
        "dance":      round(sum(dance_vals)       / len(dance_vals),      3),
        "mainstream": round(sum(mainstream_vals)  / len(mainstream_vals), 3),
    }


async def get_mood_from_tracks(tracks: list[dict]) -> dict | None:
    """
    Fetch Last.fm tags for top 10 tracks and average the mood.
    tracks: list of {"name": str, "artists": [str]}
    Returns averaged mood dict or None if Last.fm unavailable/no tags matched.
    """
    if not tracks or not settings.LASTFM_API_KEY:
        return None

    all_energy, all_valence, all_dance, all_mainstream = [], [], [], []

    for t in tracks[:10]:
        artist = t.get("artists", [""])[0]
        name   = t.get("name", "")
        if not artist or not name:
            continue

        tags = await get_track_tags(artist, name)
        mood = tags_to_mood(tags)
        if mood:
            all_energy.append(mood["energy"])
            all_valence.append(mood["valence"])
            all_dance.append(mood["dance"])
            all_mainstream.append(mood["mainstream"])

    if not all_energy:
        return None

    return {
        "energy":     round(sum(all_energy)     / len(all_energy),     3),
        "valence":    round(sum(all_valence)     / len(all_valence),    3),
        "dance":      round(sum(all_dance)       / len(all_dance),      3),
        "mainstream": round(sum(all_mainstream)  / len(all_mainstream), 3),
    }
