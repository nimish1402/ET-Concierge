"""
Chat Router — POST /chat | POST /chat/stream

Onboarding flow:
1. User messages → Groq (llama-3.3-70b-versatile) conversational replies
2. When Groq signals profile-ready, we call Groq again to extract a structured JSON profile
3. Profile + first recommendations are saved to Weaviate
4. Subsequent messages with a valid user_id → RAG mode (context-aware Q&A)
"""
import json
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from models.schemas import ChatRequest, ChatResponse
from services.llm_service import (
    chat_with_groq,
    stream_chat_groq,
    extract_profile_with_groq,
    answer_with_context,
)
from services.rag_service import retrieve_context_for_query
from services.recommendation_service import (
    score_products,
    save_recommendations,
    get_user_events,
)
from db.weaviate_client import get_client
from datetime import datetime, timezone
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)

# ── Completion detection ──────────────────────────────────────────────────────
# We check for ANY of these phrases (lowercase) in the assistant reply
COMPLETION_PHRASES = [
    "i now have a good picture of your financial goals",
    "let me build your personalized profile",
    "i have a good understanding of your",
    "i've gathered enough information",
    "i have enough information to",
    "based on our conversation, i can now",
    "let me create your personalized",
    "i now have all the information i need",
]


def _is_profiling_complete(reply: str) -> bool:
    reply_lower = reply.lower()
    return any(phrase in reply_lower for phrase in COMPLETION_PHRASES)


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Main chat endpoint. Stateless — client sends full message history each request.
    """
    # Build history list for LLM
    history = [{"role": m.role, "content": m.content} for m in req.history]
    history.append({"role": "user", "content": req.message})

    user_id = req.user_id

    # ── RAG mode: user already has profile ────────────────────────────────────
    if user_id and _user_has_profile(user_id):
        context_chunks = retrieve_context_for_query(req.message)
        profile = _get_user_profile(user_id)
        reply = answer_with_context(req.message, context_chunks, profile)
        return ChatResponse(reply=reply, user_id=user_id, profile_complete=True)

    # ── Onboarding mode: generate next conversational reply ───────────────────
    reply = chat_with_groq(history)

    # Check if Groq has signalled it has enough info
    if _is_profiling_complete(reply):
        # Include the assistant's final reply in the conversation for profiling context
        full_history = history + [{"role": "assistant", "content": reply}]
        conversation_text = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in full_history
        )

        try:
            extracted = extract_profile_with_groq(conversation_text)

            # Validate we got the required fields
            if not extracted.get("persona") or not extracted.get("risk_level"):
                raise ValueError(f"Incomplete profile extracted: {extracted}")

            new_user_id = user_id or str(uuid.uuid4())
            _save_user_profile(new_user_id, extracted)

            # Generate & persist first set of recommendations
            events = get_user_events(new_user_id)
            recs = score_products(extracted, events)
            save_recommendations(new_user_id, recs)

            logger.info(f"Profile created for user {new_user_id}: {extracted.get('persona')}")

            return ChatResponse(
                reply=reply,
                user_id=new_user_id,
                profile_complete=True,
            )

        except json.JSONDecodeError as e:
            logger.error(f"Profile JSON parse failed: {e}")
            # Ask Groq to retry with a more forceful prompt
            retry_reply = _retry_profile_extraction(conversation_text)
            if retry_reply:
                return ChatResponse(
                    reply=reply,
                    user_id=retry_reply.get("user_id"),
                    profile_complete=retry_reply.get("profile_complete", False),
                )
            # Fall through — return the reply without profile
            reply += "\n\n_(I'm having trouble saving your profile right now. Please try sending one more message.)_"

        except Exception as e:
            logger.error(f"Profile extraction failed: {e}")
            reply += "\n\n_(I'm having trouble saving your profile right now. Please try sending one more message.)_"

    return ChatResponse(reply=reply, user_id=user_id, profile_complete=False)


def _retry_profile_extraction(conversation_text: str) -> dict | None:
    """Second attempt at profile extraction with a stricter prompt."""
    try:
        extracted = extract_profile_with_groq(conversation_text)
        if not extracted.get("persona"):
            return None
        new_user_id = str(uuid.uuid4())
        _save_user_profile(new_user_id, extracted)
        events = get_user_events(new_user_id)
        recs = score_products(extracted, events)
        save_recommendations(new_user_id, recs)
        return {"user_id": new_user_id, "profile_complete": True}
    except Exception as e:
        logger.error(f"Retry profile extraction also failed: {e}")
        return None


@router.post("/stream")
async def chat_stream(req: ChatRequest):
    """
    SSE streaming endpoint — yields text/event-stream chunks for real-time UX.
    """
    history = [{"role": m.role, "content": m.content} for m in req.history]
    history.append({"role": "user", "content": req.message})

    def generate():
        for chunk in stream_chat_groq(history):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# ── Weaviate helpers ──────────────────────────────────────────────────────────

def _user_has_profile(user_id: str) -> bool:
    """Return True if the user UUID exists in the User collection."""
    client = get_client()
    try:
        collection = client.collections.get("User")
        result = collection.query.fetch_object_by_id(user_id)
        return result is not None
    except Exception as e:
        logger.warning(f"_user_has_profile check failed for {user_id}: {e}")
        return False


def _get_user_profile(user_id: str) -> dict | None:
    """Fetch a user profile dict from Weaviate."""
    client = get_client()
    try:
        collection = client.collections.get("User")
        result = collection.query.fetch_object_by_id(user_id)
        if result:
            props = result.properties
            return {
                "persona": props.get("persona", ""),
                "risk_level": props.get("risk_level", ""),
                "goals": json.loads(props.get("goals", "[]")),
                "interests": json.loads(props.get("interests", "[]")),
            }
    except Exception as e:
        logger.warning(f"_get_user_profile failed for {user_id}: {e}")
    return None


def _save_user_profile(user_id: str, profile: dict):
    """Persist an extracted profile to Weaviate with the given UUID."""
    client = get_client()
    collection = client.collections.get("User")
    collection.data.insert(
        properties={
            "name": profile.get("name", ""),
            "persona": profile.get("persona", ""),
            "risk_level": profile.get("risk_level", ""),
            "goals": json.dumps(profile.get("goals", [])),
            "interests": json.dumps(profile.get("interests", [])),
            "recommended_products": json.dumps(profile.get("recommended_products", [])),
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        uuid=user_id,
    )
    logger.info(f"Saved profile for user {user_id}")
