"""
Events Router — POST /events

Records user behavior events for the recommendation scoring engine.
"""
from fastapi import APIRouter, HTTPException
from models.schemas import EventRequest
from db.weaviate_client import get_client
from datetime import datetime, timezone
import json

router = APIRouter()


@router.post("")
async def log_event(req: EventRequest):
    """
    Record a user event (click, search, view, like).
    Metadata is stored as JSON string in Weaviate.
    """
    client = get_client()
    collection = client.collections.get("Event")
    try:
        uid = collection.data.insert({
            "user_id": req.user_id,
            "event_type": req.event_type,
            "metadata": json.dumps(req.metadata),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return {"status": "logged", "event_id": str(uid)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
