import httpx
import json
import logging
from config import settings

logger = logging.getLogger(__name__)
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL    = "llama-3.3-70b-versatile"


async def _call(system: str, user: str, max_tokens: int = 500, temperature: float = 0.92) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
                "max_tokens":  max_tokens,
                "temperature": temperature,
            },
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()


# ── ROAST PROMPTS ──────────────────────────────────────────────────────────────

ROAST_SYSTEMS = {
    "gentle": (
        "You are a politely passive-aggressive music critic. "
        "Gently roast someone's music taste — be subtly shady but maintain plausible deniability. "
        "2-3 sentences. Reference their actual artists. End with a backhanded compliment."
    ),
    "roasted": (
        "You are a savage music critic who roasts people like a comedy roast. "
        "Burn their music taste in 3-4 funny, specific sentences. Use their actual artist names. "
        "Be brutal but funny. No asterisks or markdown."
    ),
    "destroyed": (
        "You are an absolutely ruthless music critic with zero mercy. "
        "Absolutely destroy this person's music taste in 4-5 sentences. "
        "Be specific, personal, and hilariously devastating. Reference their top artists by name. "
        "End with something that will haunt them. No markdown."
    ),
    "courtroom": (
        "You are a stern judge presiding over a Music Taste Court. "
        "Deliver a formal courtroom verdict on this person's music taste. "
        "Use legal language mixed with music criticism. Announce the verdict, cite evidence (their artists), "
        "and deliver the sentence (musical punishment). 4-5 sentences. No markdown."
    ),
}

ROAST_CATEGORY_SYSTEMS = {
    "age": (
        "You are a music critic specializing in age-based music roasts. "
        "Roast this person based on the era of their music. "
        "If they listen to old music: retirement home jokes. "
        "If new music: basic millennial/gen-z jokes. 2-3 sentences."
    ),
    "mainstream": (
        "You are a music snob roasting a mainstream listener. "
        "Call them out for only listening to what Spotify recommends. "
        "Suggest they have no independent taste. 2-3 sentences. Be funny."
    ),
    "obsessive": (
        "You are staging a musical intervention. "
        "This person is dangerously obsessed with one artist. "
        "Write the intervention speech — concerned, dramatic, funny. 3-4 sentences."
    ),
    "sad": (
        "You are a cheerful therapist horrified by someone's depressing playlist. "
        "Comment on their sad music choices. Suggest they need sunlight and friends. 2-3 sentences."
    ),
    "energy": (
        "You are a music critic roasting someone's extreme music energy. "
        "Either too high energy (they need to calm down) or too low (do they have a pulse?). "
        "2-3 sentences. Be funny."
    ),
}


async def generate_roast(user_data: dict, severity: str = "roasted") -> str:
    system = ROAST_SYSTEMS.get(severity, ROAST_SYSTEMS["roasted"])
    prompt = (
        f"Name: {user_data.get('name', 'this person')}\n"
        f"Top artists: {user_data.get('top_artists', [])[:5]}\n"
        f"Top tracks: {user_data.get('top_tracks', [])[:5]}\n"
        f"Genres: {user_data.get('genres', [])[:5]}\n"
        f"Personality type: {user_data.get('personality_type', 'Unknown')}\n"
        f"Mood: energy={user_data.get('energy', 0.5):.0%}, happiness={user_data.get('valence', 0.5):.0%}\n"
        "Roast them."
    )
    return await _call(system, prompt)


async def generate_category_roast(user_data: dict, category: str) -> str:
    system = ROAST_CATEGORY_SYSTEMS.get(category, ROAST_CATEGORY_SYSTEMS["mainstream"])
    prompt = (
        f"Top artists: {user_data.get('top_artists', [])[:5]}\n"
        f"Top tracks: {user_data.get('top_tracks', [])[:5]}\n"
        f"Genres: {user_data.get('genres', [])[:4]}\n"
        "Write the roast."
    )
    return await _call(system, prompt)


async def generate_alibi(user_data: dict) -> str:
    system = (
        "You are a defense attorney defending someone's terrible music taste in court. "
        "Generate the most creative, absurd alibi for why their taste is actually genius. "
        "3-4 sentences. Be ridiculous but convincing."
    )
    prompt = f"Artists: {user_data.get('top_artists', [])[:4]}, Genres: {user_data.get('genres', [])[:3]}"
    return await _call(system, prompt)


async def generate_music_horoscope(user_data: dict) -> str:
    system = (
        "You are a music astrologer. Generate a weekly music horoscope based on someone's listening data. "
        "Mix astrology language with music references. Reference their actual artists/genres. "
        "Predict something absurd about their week based on their music. 3-4 sentences."
    )
    prompt = (
        f"Top artists: {user_data.get('top_artists', [])[:4]}\n"
        f"Personality: {user_data.get('personality_type')}\n"
        f"Energy: {user_data.get('energy', 0.5):.0%}\n"
        "Generate their music horoscope."
    )
    return await _call(system, prompt)


async def generate_taste_in_three_words(user_data: dict) -> str:
    system = "Respond with EXACTLY 3 words describing someone's music taste, separated by dots. Example: 'Chaotic. Nostalgic. Questionable.' No other text."
    prompt = f"Artists: {user_data.get('top_artists', [])[:3]}, Genres: {user_data.get('genres', [])[:3]}"
    return await _call(system, prompt, max_tokens=20)


# ── BATTLE PROMPTS ─────────────────────────────────────────────────────────────

async def generate_battle_verdict(user_a: dict, user_b: dict) -> dict:
    system = (
        "You are a dramatic music battle judge. Two people are competing for best music taste. "
        "Analyze both contestants and deliver a verdict. Be funny, specific, use their actual artists. "
        "Respond in this exact JSON format with no extra text:\n"
        '{"winner": "name of winner", "verdict": "2-3 sentence funny verdict", '
        '"user_a_roast": "1-2 sentence roast of user A", "user_b_roast": "1-2 sentence roast of user B", '
        '"winning_reason": "one funny sentence why winner won"}'
    )
    prompt = (
        f"Contestant A: {user_a.get('name')}\n"
        f"  Artists: {user_a.get('top_artists', [])[:4]}\n"
        f"  Genres: {user_a.get('genres', [])[:3]}\n"
        f"  Personality: {user_a.get('personality_type')}\n"
        f"  Taste score: {user_a.get('taste_score', 50)}\n\n"
        f"Contestant B: {user_b.get('name')}\n"
        f"  Artists: {user_b.get('top_artists', [])[:4]}\n"
        f"  Genres: {user_b.get('genres', [])[:3]}\n"
        f"  Personality: {user_b.get('personality_type')}\n"
        f"  Taste score: {user_b.get('taste_score', 50)}\n\n"
        "Who has better taste? Deliver the verdict."
    )
    raw = await _call(system, prompt, max_tokens=400)
    try:
        clean = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception:
        winner = user_a["name"] if user_a.get("taste_score", 0) >= user_b.get("taste_score", 0) else user_b["name"]
        return {
            "winner": winner,
            "verdict": f"After careful deliberation, {winner} wins. The other person should listen to more music.",
            "user_a_roast": f"{user_a['name']}'s taste is... something.",
            "user_b_roast": f"{user_b['name']}'s taste is... also something.",
            "winning_reason": "Pure vibes, really.",
        }


# ── SQUAD PROMPTS ──────────────────────────────────────────────────────────────

async def generate_squad_roast(members: list[dict]) -> str:
    system = (
        "You are a roast comedian at a music-themed roast dinner. "
        "Roast an entire friend group's combined music taste. "
        "Reference each person by name with a specific burn. "
        "End with a devastating group observation. 5-7 sentences total. No markdown."
    )
    members_text = "\n".join([
        f"- {m['display_name']}: listens to {m.get('top_artists', ['???'])[:2]}, personality: {m.get('personality_type', '???')}"
        for m in members
    ])
    prompt = f"The friend group:\n{members_text}\n\nRoast them all."
    return await _call(system, prompt, max_tokens=400)


async def generate_compatibility_tagline(user_a: dict, user_b: dict, score: float) -> str:
    system = (
        "Generate ONE punchy sentence describing two people's music compatibility. "
        "Be funny and specific. Reference their artists/genres. No markdown."
    )
    prompt = (
        f"{user_a.get('name')} (likes {user_a.get('top_artists', ['???'])[:2]}) "
        f"vs {user_b.get('name')} (likes {user_b.get('top_artists', ['???'])[:2]}). "
        f"Compatibility: {score:.0f}%."
    )
    return await _call(system, prompt, max_tokens=80)


from typing import List
