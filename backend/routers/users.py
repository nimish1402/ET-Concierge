"""
Users Router — GET /user/{id}
"""
import json
from fastapi import APIRouter, HTTPException
from db.weaviate_client import get_client

router = APIRouter()


@router.get("/{user_id}")
async def get_user(user_id: str):
    """Retrieve full user object from Weaviate."""
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
