"""
Recommendations Router — GET /recommendations?user_id=...
                        POST /recommendations/refresh

Generates and retrieves personalized product recommendations.
"""
import json
from fastapi import APIRouter, HTTPException, Query
from services.recommendation_service import (
    score_products,
    save_recommendations,
    get_recommendations,
    get_user_events,
)
from services.llm_service import generate_recommendation_reasons
from db.weaviate_client import get_client

router = APIRouter()


@router.get("")
async def get_user_recommendations(user_id: str = Query(...)):
    """Retrieve stored recommendations for a user."""
    recs = get_recommendations(user_id)
    if not recs:
        raise HTTPException(status_code=404, detail="No recommendations found. Complete onboarding first.")
    return {"user_id": user_id, "recommendations": recs}


@router.post("/refresh")
async def refresh_recommendations(user_id: str = Query(...)):
    """
    Re-score recommendations based on latest profile & events.
    Optionally enriches reasons with Gemini explanations.
    """
    # Fetch user profile
    client = get_client()
    collection = client.collections.get("User")
    result = collection.query.fetch_object_by_id(user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")

    props = result.properties
    profile = {
        "persona": props.get("persona", ""),
        "risk_level": props.get("risk_level", "moderate"),
        "goals": json.loads(props.get("goals", "[]")),
        "interests": json.loads(props.get("interests", "[]")),
    }

    # Fetch events for behavior scoring
    events = get_user_events(user_id)

    # Score and rank products
    scored = score_products(profile, events)

    # Enrich with LLM-generated reasons (non-blocking if it fails)
    try:
        reasons = generate_recommendation_reasons(
            profile=profile,
            behavior=events[:5],
            products=[r["product"] for r in scored],
        )
        for r in scored:
            r["reason"] = reasons.get(r["product"], f"Matches your {profile['persona']} profile")
    except Exception:
        for r in scored:
            r["reason"] = f"Recommended based on your {profile['persona']} profile and interests"

    # Persist
    save_recommendations(user_id, scored)
    return {"user_id": user_id, "recommendations": scored}
