from typing import List, Dict
from collections import Counter
import re

# ── Artist → Indian/Regional category map ────────────────────────────────────
# Covers 60+ artists. Keys are lowercase for case-insensitive lookup.
ARTIST_CATEGORY_MAP: Dict[str, str] = {
    # Tamil Film Music
    "ar rahman":            "tamil film music",
    "a.r. rahman":          "tamil film music",
    "harris jayaraj":       "tamil film music",
    "yuvan shankar raja":   "tamil film music",
    "anirudh ravichander":  "tamil film music",
    "anirudh":              "tamil film music",
    "d. imman":             "tamil film music",
    "d imman":              "tamil film music",
    "gv prakash kumar":     "tamil film music",
    "gv prakash":           "tamil film music",
    "santhosh narayanan":   "tamil film music",
    "sean roldan":          "tamil film music",
    "hiphop tamizha":       "tamil hip-hop",
    "hiphop tamizha adhi":  "tamil hip-hop",
    "sj suryah":            "tamil film music",
    "vijay antony":         "tamil film music",
    "deva":                 "tamil film music",
    "ilaiyaraaja":          "tamil film music (classic)",
    "ilayaraja":            "tamil film music (classic)",
    "m. s. viswanathan":    "tamil film music (classic)",
    "ms viswanathan":       "tamil film music (classic)",
    "s. a. rajkumar":       "tamil film music (classic)",
    "sa rajkumar":          "tamil film music (classic)",
    "james vasanthan":      "tamil film music",
    "simon":                "tamil film music",
    "thaman s":             "telugu film music",

    # Tamil Independent / Hip-Hop
    "arivu":                "tamil hip-hop",
    "pb":                   "tamil hip-hop",
    "pa ranjith":           "tamil independent",
    "yogi b":               "tamil hip-hop",
    "natchatra":            "tamil independent",
    "leon james":           "tamil independent/film",

    # Tamil Devotional / Classical
    "bombay sisters":       "devotional",
    "m.s. subbulakshmi":    "indian classical/film",
    "ms subbulakshmi":      "indian classical/film",
    "m. s. subbulakshmi":   "indian classical/film",
    "k.j. yesudas":         "spiritual/film",
    "kj yesudas":           "spiritual/film",
    "s.p. balasubrahmanyam": "indian film/ghazal",
    "sp balasubrahmanyam":  "indian film/ghazal",
    "spb":                  "indian film/ghazal",

    # Telugu Film Music
    "s. s. thaman":         "telugu film music",
    "ss thaman":            "telugu film music",
    "devi sri prasad":      "telugu film music",
    "dsp":                  "telugu film music",
    "mickey j meyer":       "telugu film music",
    "mani sharma":          "telugu film music",
    "anup rubens":          "telugu film music",
    "radhan":               "telugu film music",
    "vishal-shekhar":       "hindi film music",

    # Kannada / Malayalam Film Music
    "ravi basrur":          "kannada film music",
    "arjun janya":          "kannada film music",
    "v. harikrishna":       "kannada film music",
    "v harikrishna":        "kannada film music",
    "hamsalekha":           "kannada film music",
    "raju anantaswamy":     "kannada/tamil film",
    "bijibal":              "malayalam film music",
    "shaan rahman":         "malayalam film music",
    "m jayachandran":       "malayalam film music",
    "gopi sundar":          "malayalam film music",
    "vidyasagar":           "kannada/tamil film",

    # Hindi / Bollywood Film Music
    "shankar-ehsaan-loy":   "hindi film music",
    "pritam":               "hindi film music",
    "amit trivedi":         "hindi film music",
    "vishal bhardwaj":      "hindi film music",
    "a.r. rahman":          "hindi film music",
    "sonu nigam":           "hindi film music",
    "arijit singh":         "hindi film music",
    "shreya ghoshal":       "hindi film music",
    "armaan malik":         "hindi pop",
    "neha kakkar":          "hindi pop",
    "badshah":              "hindi hip-hop",
    "yo yo honey singh":    "hindi hip-hop",
    "divine":               "hindi hip-hop",
    "nucleya":              "hindi electronic",
    "ritviz":               "hindi independent",
    "prateek kuhad":        "hindi independent",
    "when chai met toast":  "hindi independent",

    # Punjabi
    "diljit dosanjh":       "punjabi",
    "ap dhillon":           "punjabi",
    "shubh":                "punjabi",
    "sidhu moosewala":      "punjabi",
    "amrit maan":           "punjabi",
    "jazzy b":              "punjabi",
    "guru randhawa":        "punjabi pop",

    # Devotional / Spiritual
    "shankar mahadevan":    "devotional",
    "hariharan":            "devotional",
    "hari prasad chaurasia": "indian classical/film",
    "zakir hussain":        "indian classical/film",
    "pandit jasraj":        "indian classical/film",
    "lata mangeshkar":      "hindi film music",
    "asha bhosle":          "hindi film music",
    "kishore kumar":        "hindi film music",
    "mohammed rafi":        "hindi film music",
    "hemant kumar":         "hindi film music",
}

# Map our Indian category labels → mood values so the rest of the scoring
# pipeline works without any other changes.
INDIAN_CATEGORY_MOOD: Dict[str, Dict[str, float]] = {
    "tamil film music":          {"energy": 0.72, "valence": 0.68, "dance": 0.72, "mainstream": 0.55},
    "tamil film music (classic)":{"energy": 0.58, "valence": 0.65, "dance": 0.60, "mainstream": 0.40},
    "tamil film (classic)":      {"energy": 0.58, "valence": 0.65, "dance": 0.60, "mainstream": 0.40},
    "tamil hip-hop":             {"energy": 0.82, "valence": 0.60, "dance": 0.80, "mainstream": 0.45},
    "tamil independent":         {"energy": 0.55, "valence": 0.58, "dance": 0.55, "mainstream": 0.28},
    "tamil independent/film":    {"energy": 0.60, "valence": 0.60, "dance": 0.60, "mainstream": 0.35},
    "telugu film music":         {"energy": 0.75, "valence": 0.70, "dance": 0.74, "mainstream": 0.52},
    "kannada film music":        {"energy": 0.70, "valence": 0.66, "dance": 0.70, "mainstream": 0.48},
    "kannada/tamil film":        {"energy": 0.70, "valence": 0.66, "dance": 0.70, "mainstream": 0.48},
    "malayalam film music":      {"energy": 0.68, "valence": 0.66, "dance": 0.68, "mainstream": 0.48},
    "hindi film music":          {"energy": 0.70, "valence": 0.68, "dance": 0.72, "mainstream": 0.68},
    "hindi pop":                 {"energy": 0.72, "valence": 0.70, "dance": 0.74, "mainstream": 0.72},
    "hindi hip-hop":             {"energy": 0.80, "valence": 0.58, "dance": 0.78, "mainstream": 0.60},
    "hindi independent":         {"energy": 0.52, "valence": 0.60, "dance": 0.52, "mainstream": 0.32},
    "hindi electronic":          {"energy": 0.82, "valence": 0.62, "dance": 0.82, "mainstream": 0.50},
    "punjabi":                   {"energy": 0.80, "valence": 0.72, "dance": 0.82, "mainstream": 0.62},
    "punjabi pop":               {"energy": 0.76, "valence": 0.72, "dance": 0.78, "mainstream": 0.68},
    "devotional":                {"energy": 0.45, "valence": 0.72, "dance": 0.40, "mainstream": 0.32},
    "spiritual/film":            {"energy": 0.50, "valence": 0.70, "dance": 0.45, "mainstream": 0.38},
    "indian classical/film":     {"energy": 0.38, "valence": 0.60, "dance": 0.32, "mainstream": 0.22},
    "indian film/ghazal":        {"energy": 0.48, "valence": 0.65, "dance": 0.45, "mainstream": 0.42},
}


def get_artist_categories(artist_names: List[str]) -> Counter:
    """
    Map a list of artist names to Indian/regional music categories.
    Returns a Counter of {category: frequency} for artists that are in
    ARTIST_CATEGORY_MAP. Unknown artists are silently skipped (not
    lumped into 'Other') so they don't pollute the genre list.
    """
    counts: Counter = Counter()
    for name in artist_names:
        key = name.lower().strip()
        category = ARTIST_CATEGORY_MAP.get(key)
        if category:
            counts[category] += 1
    return counts


# ── Genre mood map (derived from genre names, no Spotify audio-features API) ──
GENRE_MOOD: Dict[str, Dict[str, float]] = {
    "hip-hop": {"energy": 0.80, "valence": 0.60, "dance": 0.82, "mainstream": 0.75},
    "rap": {"energy": 0.78, "valence": 0.55, "dance": 0.80, "mainstream": 0.72},
    "trap": {"energy": 0.82, "valence": 0.48, "dance": 0.78, "mainstream": 0.65},
    "pop": {"energy": 0.72, "valence": 0.70, "dance": 0.75, "mainstream": 0.90},
    "dance pop": {"energy": 0.78, "valence": 0.72, "dance": 0.83, "mainstream": 0.88},
    "r&b": {"energy": 0.62, "valence": 0.60, "dance": 0.74, "mainstream": 0.70},
    "soul": {"energy": 0.58, "valence": 0.65, "dance": 0.68, "mainstream": 0.55},
    "rock": {"energy": 0.82, "valence": 0.50, "dance": 0.55, "mainstream": 0.65},
    "indie": {"energy": 0.60, "valence": 0.55, "dance": 0.58, "mainstream": 0.25},
    "alternative": {"energy": 0.65, "valence": 0.48, "dance": 0.55, "mainstream": 0.35},
    "electronic": {"energy": 0.85, "valence": 0.62, "dance": 0.85, "mainstream": 0.60},
    "edm": {"energy": 0.88, "valence": 0.65, "dance": 0.88, "mainstream": 0.72},
    "classical": {"energy": 0.28, "valence": 0.55, "dance": 0.25, "mainstream": 0.30},
    "jazz": {"energy": 0.42, "valence": 0.62, "dance": 0.52, "mainstream": 0.20},
    "metal": {"energy": 0.95, "valence": 0.35, "dance": 0.42, "mainstream": 0.30},
    "folk": {"energy": 0.38, "valence": 0.58, "dance": 0.40, "mainstream": 0.20},
    "country": {"energy": 0.65, "valence": 0.68, "dance": 0.62, "mainstream": 0.60},
    "latin": {"energy": 0.78, "valence": 0.75, "dance": 0.88, "mainstream": 0.75},
    "reggaeton": {"energy": 0.80, "valence": 0.72, "dance": 0.88, "mainstream": 0.70},
    "afrobeats": {"energy": 0.78, "valence": 0.76, "dance": 0.86, "mainstream": 0.55},
    "k-pop": {"energy": 0.75, "valence": 0.72, "dance": 0.78, "mainstream": 0.70},
    "bollywood": {"energy": 0.72, "valence": 0.70, "dance": 0.74, "mainstream": 0.65},
    "tamil": {"energy": 0.70, "valence": 0.68, "dance": 0.72, "mainstream": 0.55},
    "telugu": {"energy": 0.70, "valence": 0.68, "dance": 0.72, "mainstream": 0.52},
    "hindi": {"energy": 0.68, "valence": 0.66, "dance": 0.70, "mainstream": 0.60},
    "lo-fi": {"energy": 0.30, "valence": 0.52, "dance": 0.48, "mainstream": 0.45},
    "ambient": {"energy": 0.22, "valence": 0.50, "dance": 0.28, "mainstream": 0.15},
    "punk": {"energy": 0.90, "valence": 0.45, "dance": 0.52, "mainstream": 0.30},
    "blues": {"energy": 0.48, "valence": 0.42, "dance": 0.50, "mainstream": 0.20},
    "sad": {"energy": 0.35, "valence": 0.25, "dance": 0.35, "mainstream": 0.50},
    "chill": {"energy": 0.32, "valence": 0.58, "dance": 0.45, "mainstream": 0.50},
    "workout": {"energy": 0.90, "valence": 0.62, "dance": 0.75, "mainstream": 0.60},
    "devotional": {"energy": 0.45, "valence": 0.72, "dance": 0.40, "mainstream": 0.30},
    "film": {"energy": 0.60, "valence": 0.60, "dance": 0.58, "mainstream": 0.55},
    # Indian / Regional
    "filmi":            {"energy": 0.68, "valence": 0.66, "dance": 0.70, "mainstream": 0.65},
    "desi pop":         {"energy": 0.72, "valence": 0.70, "dance": 0.74, "mainstream": 0.65},
    "desi":             {"energy": 0.70, "valence": 0.68, "dance": 0.72, "mainstream": 0.62},
    "kollywood":        {"energy": 0.70, "valence": 0.68, "dance": 0.72, "mainstream": 0.55},
    "tollywood":        {"energy": 0.70, "valence": 0.68, "dance": 0.72, "mainstream": 0.52},
    "malayalam":        {"energy": 0.68, "valence": 0.66, "dance": 0.70, "mainstream": 0.50},
    "kannada":          {"energy": 0.68, "valence": 0.66, "dance": 0.70, "mainstream": 0.48},
    "bengali":          {"energy": 0.62, "valence": 0.65, "dance": 0.65, "mainstream": 0.50},
    "marathi":          {"energy": 0.65, "valence": 0.66, "dance": 0.68, "mainstream": 0.48},
    "punjabi":          {"energy": 0.80, "valence": 0.72, "dance": 0.82, "mainstream": 0.62},
    "bhangra":          {"energy": 0.85, "valence": 0.78, "dance": 0.88, "mainstream": 0.55},
    "sufi":             {"energy": 0.42, "valence": 0.68, "dance": 0.45, "mainstream": 0.38},
    "carnatic":         {"energy": 0.45, "valence": 0.62, "dance": 0.38, "mainstream": 0.22},
    "hindustani":       {"energy": 0.42, "valence": 0.60, "dance": 0.35, "mainstream": 0.20},
    "indian classical": {"energy": 0.38, "valence": 0.60, "dance": 0.32, "mainstream": 0.20},
    "indian pop":       {"energy": 0.70, "valence": 0.68, "dance": 0.72, "mainstream": 0.65},
    # Modern / Trap / Urban
    "trap soul":        {"energy": 0.65, "valence": 0.45, "dance": 0.72, "mainstream": 0.70},
    "melodic rap":      {"energy": 0.75, "valence": 0.52, "dance": 0.76, "mainstream": 0.65},
    "drill":            {"energy": 0.82, "valence": 0.38, "dance": 0.75, "mainstream": 0.60},
    "phonk":            {"energy": 0.85, "valence": 0.42, "dance": 0.78, "mainstream": 0.55},
    "urban contemporary": {"energy": 0.68, "valence": 0.60, "dance": 0.75, "mainstream": 0.75},
    "quiet storm":      {"energy": 0.45, "valence": 0.58, "dance": 0.55, "mainstream": 0.55},
    # Electronic subgenres
    "future bass":      {"energy": 0.85, "valence": 0.70, "dance": 0.85, "mainstream": 0.60},
    "dubstep":          {"energy": 0.90, "valence": 0.48, "dance": 0.78, "mainstream": 0.55},
    "drum and bass":    {"energy": 0.90, "valence": 0.52, "dance": 0.82, "mainstream": 0.42},
    "house":            {"energy": 0.82, "valence": 0.65, "dance": 0.90, "mainstream": 0.60},
    "techno":           {"energy": 0.88, "valence": 0.48, "dance": 0.85, "mainstream": 0.35},
    "trance":           {"energy": 0.86, "valence": 0.65, "dance": 0.82, "mainstream": 0.45},
    "synthwave":        {"energy": 0.72, "valence": 0.58, "dance": 0.70, "mainstream": 0.40},
    "retrowave":        {"energy": 0.70, "valence": 0.58, "dance": 0.68, "mainstream": 0.38},
    "vaporwave":        {"energy": 0.35, "valence": 0.55, "dance": 0.48, "mainstream": 0.28},
    "grime":            {"energy": 0.85, "valence": 0.45, "dance": 0.75, "mainstream": 0.48},
    "uk rap":           {"energy": 0.80, "valence": 0.50, "dance": 0.75, "mainstream": 0.52},
    # Soft / Acoustic
    "bedroom pop":      {"energy": 0.42, "valence": 0.60, "dance": 0.50, "mainstream": 0.30},
    "dream pop":        {"energy": 0.40, "valence": 0.62, "dance": 0.48, "mainstream": 0.28},
    "shoegaze":         {"energy": 0.58, "valence": 0.45, "dance": 0.42, "mainstream": 0.22},
    "acoustic":         {"energy": 0.38, "valence": 0.60, "dance": 0.42, "mainstream": 0.45},
    "singer-songwriter":{"energy": 0.40, "valence": 0.58, "dance": 0.40, "mainstream": 0.42},
    # Other
    "afro pop":         {"energy": 0.78, "valence": 0.76, "dance": 0.86, "mainstream": 0.60},
    "dancehall":        {"energy": 0.80, "valence": 0.72, "dance": 0.88, "mainstream": 0.62},
    "bachata":          {"energy": 0.68, "valence": 0.70, "dance": 0.85, "mainstream": 0.58},
    "cumbia":           {"energy": 0.72, "valence": 0.72, "dance": 0.86, "mainstream": 0.55},
    "emo":              {"energy": 0.72, "valence": 0.30, "dance": 0.45, "mainstream": 0.42},
    "post-rock":        {"energy": 0.65, "valence": 0.45, "dance": 0.38, "mainstream": 0.22},
}

# ── Funny personality types ──
PERSONALITY_TYPES = {
    "😭 The Crier": "Your playlist is basically a therapy session. You listen to sad songs at 2am and call it self-care.",
    "🏋️ The Gym Rat": "Every song you own could feature in a gym montage. Do you even own any slow songs?",
    "👴 The Boomer": "Your music taste is frozen in a specific decade. You peaked musically and you know it.",
    "🌿 The Pretentious One": "Nobody has heard of your artists. That's the point, isn't it?",
    "🎭 The Chameleon": "Different genre every week. You have no idea who you are and your playlist proves it.",
    "💘 The Romantic": "Every song is a love story. You're either deeply in love or deeply in denial.",
    "🥷 The Ghost": "You barely listen but when you do, the choices are... interesting.",
    "🎰 The Randomizer": "No pattern whatsoever. A playlist generated by throwing darts at a Spotify wall.",
    "😤 The Obsessive": "One artist. Constantly. Repeatedly. Exclusively. Please seek help.",
    "🤡 The Mainstream": "You only listen to what Spotify tells you to. A walking algorithm.",
    "🔥 The Hype Beast": "Only bangers. Only energy. You would give yourself a headache at a library.",
    "😴 The Background Listener": "Your music is so chill it barely qualifies as music. Elevator banger.",
}

# ── Squad awards ──
SQUAD_AWARDS = {
    "👑 Music Overlord": "Highest overall taste score in the squad",
    "💀 Needs Therapy": "Most sad/depressing music detected",
    "🤡 Spotify's Puppet": "Most mainstream listener",
    "🧅 Too Cool For This": "Most obscure/underground taste",
    "⏰ Stuck in Time": "Oldest music taste in the squad",
    "🔁 One-Trick Pony": "Most obsessed with a single artist",
    "🌍 World Citizen": "Most genre diversity",
    "🔥 Hype Beast": "Highest energy music",
    "😴 Background Music": "Most chill/ambient taste",
    "🎭 Most Chaotic": "Least consistent music taste",
}


def _match_genre(genre: str) -> Dict[str, float] | None:
    """
    Try to match a single genre string against GENRE_MOOD or INDIAN_CATEGORY_MOOD.
    Strategy:
      1. Check INDIAN_CATEGORY_MOOD first (exact match for our custom categories)
      2. Exact substring match against GENRE_MOOD keys
      3. Word-level match / averaged partial match
    Returns a mood dict or None.
    """
    gl = genre.lower().strip()

    # 1. Exact match in Indian category map
    if gl in INDIAN_CATEGORY_MOOD:
        return INDIAN_CATEGORY_MOOD[gl]

    # 2. Exact substring — first key that appears inside the genre string
    for key, mood in GENRE_MOOD.items():
        if key in gl:
            return mood

    # 3. Word-level — collect mood for every word that hits a key
    words = re.split(r"[\s\-_&/]+", gl)
    hits: list[Dict] = []
    for word in words:
        if len(word) < 3:
            continue
        for key, mood in GENRE_MOOD.items():
            if word == key or word in key or key in word:
                hits.append(mood)
                break

    if not hits:
        return None

    return {
        "energy":     round(sum(h["energy"]     for h in hits) / len(hits), 3),
        "valence":    round(sum(h["valence"]    for h in hits) / len(hits), 3),
        "dance":      round(sum(h["dance"]      for h in hits) / len(hits), 3),
        "mainstream": round(sum(h["mainstream"] for h in hits) / len(hits), 3),
    }


def derive_mood_from_genres(genres: List[str]) -> Dict[str, float]:
    """Derive mood scores purely from user's genre list with smart matching."""
    if not genres:
        return {"energy": 0.60, "valence": 0.55, "dance": 0.60, "mainstream": 0.55}

    energy_vals, valence_vals, dance_vals, mainstream_vals = [], [], [], []

    for genre in genres:
        mood = _match_genre(genre)
        if mood:
            energy_vals.append(mood["energy"])
            valence_vals.append(mood["valence"])
            dance_vals.append(mood["dance"])
            mainstream_vals.append(mood["mainstream"])

    if not energy_vals:
        return {"energy": 0.60, "valence": 0.55, "dance": 0.60, "mainstream": 0.55}

    return {
        "energy":     round(sum(energy_vals)     / len(energy_vals),     3),
        "valence":    round(sum(valence_vals)     / len(valence_vals),    3),
        "dance":      round(sum(dance_vals)       / len(dance_vals),      3),
        "mainstream": round(sum(mainstream_vals)  / len(mainstream_vals), 3),
    }


def get_personality_type(
    mood: Dict[str, float],
    top_artists: List[str],
    genres: List[str],
) -> str:
    energy      = mood.get("energy",     0.5)
    valence     = mood.get("valence",    0.5)
    mainstream  = mood.get("mainstream", 0.5)

    # Check for one-artist obsession
    if top_artists and len(set(top_artists[:5])) <= 2:
        return "😤 The Obsessive"

    if valence < 0.38:
        return "😭 The Crier"
    if energy > 0.82:
        return "🔥 The Hype Beast"
    if energy < 0.30:
        return "😴 The Background Listener"
    if mainstream > 0.82:
        return "🤡 The Mainstream"
    if mainstream < 0.28:
        return "🌿 The Pretentious One"
    if energy > 0.75 and valence < 0.45:
        return "🏋️ The Gym Rat"
    if valence > 0.72:
        return "💘 The Romantic"

    genre_str = " ".join(genres).lower()
    decade_genres = ["oldies", "classic", "70s", "80s", "90s", "retro", "vintage"]
    if any(d in genre_str for d in decade_genres):
        return "👴 The Boomer"

    if len(set(genres)) > 8:
        return "🎭 The Chameleon"

    return "🎰 The Randomizer"


def compute_taste_score(
    mood: Dict[str, float],
    genres: List[str],
    top_artists: List[str],
    top_tracks: List[dict],
) -> Dict:
    """
    Compute a fun 'taste score' based purely on user's own data.
    Higher score = more 'interesting' taste (diverse, energetic, unique).
    """
    unique_genres = len(set(genres))
    diversity = min(unique_genres / 10, 1.0) * 100

    uniqueness = (1 - mood.get("mainstream", 0.5)) * 100

    energy_score = mood.get("energy", 0.5) * 100

    if top_artists:
        artist_counts = {}
        for t in top_tracks:
            for a in t.get("artists", []):
                artist_counts[a] = artist_counts.get(a, 0) + 1
        top_artist_dominance = max(artist_counts.values(), default=1) / max(len(top_tracks), 1)
        consistency = (1 - top_artist_dominance) * 100
    else:
        consistency = 50

    overall = round(
        diversity    * 0.35 +
        uniqueness   * 0.30 +
        energy_score * 0.20 +
        consistency  * 0.15,
        1
    )

    return {
        "overall":      overall,
        "diversity":    round(diversity,    1),
        "uniqueness":   round(uniqueness,   1),
        "energy_score": round(energy_score, 1),
        "consistency":  round(consistency,  1),
    }


def detect_intervention(top_artists: List[str], top_tracks: List[dict]) -> Dict:
    """Check if user is obsessed with one artist."""
    if not top_artists or not top_tracks:
        return {"needed": False}

    artist_counts: Dict[str, int] = {}
    for t in top_tracks:
        for a in t.get("artists", []):
            artist_counts[a] = artist_counts.get(a, 0) + 1

    if not artist_counts:
        return {"needed": False}

    top_artist = max(artist_counts, key=artist_counts.get)
    top_count  = artist_counts[top_artist]
    pct        = round(top_count / len(top_tracks) * 100)

    return {
        "needed":  pct >= 35,
        "artist":  top_artist,
        "pct":     pct,
        "message": f"You've listened to {top_artist} in {pct}% of your top tracks. This is not healthy.",
    }


def compute_squad_awards(members: List[Dict]) -> List[Dict]:
    """Assign funny awards to squad members based on their data."""
    if not members:
        return []

    awards = []

    best = max(members, key=lambda m: m["scores"]["overall"])
    awards.append({"award": "👑 Music Overlord", "user": best["display_name"], "reason": f"Taste score: {best['scores']['overall']}"})

    saddest = min(members, key=lambda m: m["mood"]["valence"])
    awards.append({"award": "💀 Needs Therapy", "user": saddest["display_name"], "reason": f"Happiness score: {round(saddest['mood']['valence']*100)}%"})

    most_mainstream = max(members, key=lambda m: m["mood"]["mainstream"])
    awards.append({"award": "🤡 Spotify's Puppet", "user": most_mainstream["display_name"], "reason": f"Mainstream score: {round(most_mainstream['mood']['mainstream']*100)}%"})

    most_unique = min(members, key=lambda m: m["mood"]["mainstream"])
    awards.append({"award": "🧅 Too Cool For This", "user": most_unique["display_name"], "reason": f"Uniqueness: {round((1-most_unique['mood']['mainstream'])*100)}%"})

    most_energetic = max(members, key=lambda m: m["mood"]["energy"])
    awards.append({"award": "🔥 Hype Beast", "user": most_energetic["display_name"], "reason": f"Energy: {round(most_energetic['mood']['energy']*100)}%"})

    most_chill = min(members, key=lambda m: m["mood"]["energy"])
    awards.append({"award": "😴 Background Music", "user": most_chill["display_name"], "reason": f"Energy: {round(most_chill['mood']['energy']*100)}%"})

    most_diverse = max(members, key=lambda m: len(set(m.get("genres", []))))
    awards.append({"award": "🌍 World Citizen", "user": most_diverse["display_name"], "reason": f"{len(set(most_diverse.get('genres', [])))} unique genres"})

    for m in members:
        if m.get("intervention", {}).get("needed"):
            awards.append({
                "award":  "🔁 One-Trick Pony",
                "user":   m["display_name"],
                "reason": m["intervention"]["message"],
            })
            break

    return awards
