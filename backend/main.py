"""
ET AI Concierge - FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from db.weaviate_client import init_weaviate_schema
from routers import chat, profile, recommendations, events, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize Weaviate schema on startup."""
    init_weaviate_schema()
    yield


app = FastAPI(
    title="ET AI Concierge API",
    description="Intelligent financial assistant powered by ET ecosystem",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ET AI Concierge"}


# Register routers
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(profile.router, prefix="/profile", tags=["Profile"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(users.router, prefix="/user", tags=["Users"])
