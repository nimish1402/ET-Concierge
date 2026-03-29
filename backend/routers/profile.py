"""
Profile Router — POST /profile/init, GET /profile/{user_id}

Allows explicit profile creation (e.g., from a structured form).
"""
import json
from fastapi import APIRouter, HTTPException
from models.schemas import ProfileInitRequest
from db.weaviate_client import get_client
from datetime import datetime, timezone

router = APIRouter()


@router.post("/init")
async def init_profile(req: ProfileInitRequest):
    """Create or update a user profile from structured data."""
    client = get_client()
    collection = client.collections.get("User")
    now = datetime.now(timezone.utc).isoformat()

    try:
        collection.data.insert(
            properties={
                "name": req.name,
                "persona": req.profile.persona,
                "risk_level": req.profile.risk_level,
                "goals": json.dumps(req.profile.goals),
                "interests": json.dumps(req.profile.interests),
                "recommended_products": json.dumps(req.profile.recommended_products),
                "created_at": now,
            },
            uuid=req.user_id,
        )
        return {"status": "created", "user_id": req.user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}")
async def get_profile(user_id: str):
    """Retrieve user profile by ID."""
    client = get_client()
    collection = client.collections.get("User")
    try:
        result = collection.query.fetch_object_by_id(user_id)
        if result is None:
            raise HTTPException(status_code=404, detail="User not found")
        props = result.properties
        return {
            "id": user_id,
            "name": props.get("name", ""),
            "persona": props.get("persona", ""),
            "risk_level": props.get("risk_level", ""),
            "goals": json.loads(props.get("goals", "[]")),
            "interests": json.loads(props.get("interests", "[]")),
            "recommended_products": json.loads(props.get("recommended_products", "[]")),
            "created_at": props.get("created_at", ""),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
