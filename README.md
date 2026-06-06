# Auracle v2 🎵🔥
### *Find out who has the worst taste in your friend group*

A fun, social music roast app powered by Spotify + Groq AI.

---

## Features

| Feature | Description |
|---|---|
| 🔥 **Get Roasted** | 4 severity levels (Gentle → Destroyed), 5 roast categories, alibi generator |
| ⚔️ **Taste Battle** | 1v1 — AI judge delivers verdict with individual roasts |
| 👥 **Squad Mode** | Up to 4 friends, awards ceremony, group roast, compatibility scores |
| 🪪 **Vibe Card** | Downloadable PNG with your music personality |
| 🔮 **Horoscope** | AI-generated music horoscope based on YOUR data only |

## Data Policy
- ✅ Only your own Spotify data — no global benchmarks
- ✅ Your actual top artists, tracks, genres
- ❌ No deprecated audio-features API
- ❌ No external comparisons

## Tech Stack
```
Frontend  : React 18 + Vite + TailwindCSS + Framer Motion
Backend   : FastAPI + SQLAlchemy + Supabase (PostgreSQL)
Cache     : Redis (Upstash)
Auth      : Spotify OAuth 2.0 + JWT
AI        : Groq API (LLaMA 3.3 70B)
Deploy    : Render (backend + frontend static)
```

## Setup

### 1. Copy env
```bash
cp .env.example .env
# Fill in all values
```

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```

## Render Deployment

### Backend (Web Service)
- Root Directory: `auracle_v2/backend`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend (Static Site)
- Root Directory: `auracle_v2/frontend`
- Build: `npm install && npm run build`
- Publish: `dist`
- Rewrite: `/* → /index.html`

### Environment Variables
Set in Render dashboard (backend service):
```
SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI
JWT_SECRET_KEY
SUPABASE_DB_URL
REDIS_URL
GROQ_API_KEY
BACKEND_URL, FRONTEND_URL, ALLOWED_ORIGINS
ENV=production
```

Frontend (static site) only needs:
```
VITE_API_URL=https://your-backend.onrender.com
```

## Squad Roast Severity Levels
| Level | Vibe |
|---|---|
| 😊 Gentle | Politely passive-aggressive |
| 🔥 Roasted | Standard funny burns |
| 💀 Destroyed | Absolutely no mercy |
| 👨‍⚖️ Courtroom | Formal legal verdict |

## Squad Awards
👑 Music Overlord · 💀 Needs Therapy · 🤡 Spotify's Puppet · 🧅 Too Cool For This
🔥 Hype Beast · 😴 Background Music · 🌍 World Citizen · 🔁 One-Trick Pony
