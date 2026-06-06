from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from routers import auth, profile, roast, battle, squad
from services.database import init_db
from services.redis_client import init_redis
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_redis()
    yield


app = FastAPI(
    title="Auracle API",
    description="The Music Roast App API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"https://.*\.onrender\.com|https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,    prefix="/auth",    tags=["Auth"])
app.include_router(profile.router, prefix="/profile", tags=["Profile"])
app.include_router(roast.router,   prefix="/roast",   tags=["Roast"])
app.include_router(battle.router,  prefix="/battle",  tags=["Battle"])
app.include_router(squad.router,   prefix="/squad",   tags=["Squad"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Auracle v2", "env": settings.ENV}
