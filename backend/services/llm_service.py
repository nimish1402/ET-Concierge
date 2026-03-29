"""
LLM Service — Groq only (llama-3.3-70b-versatile)

All LLM tasks (chat, profiling, reasoning, RAG answers) use Groq's free tier.
"""
import json
import re
from groq import Groq
from config import settings

# Single Groq client used everywhere
groq_client = Groq(api_key=settings.GROQ_API_KEY)
GROQ_MODEL = "llama-3.3-70b-versatile"


# ──────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPTS
# ──────────────────────────────────────────────────────────────────────────────

CONCIERGE_SYSTEM_PROMPT = """You are ET AI Concierge, a friendly financial assistant for Economic Times.
Your job: learn about the user's financial situation in a natural 5-7 question conversation.
Ask ONE question at a time. Topics to cover:
1. Name / age range
2. Current occupation / income bracket
3. Financial goals (short & long term)
4. Existing investments (stocks, MF, FD, crypto, real estate)
5. Risk comfort level (scale 1-5)
6. Immediate financial needs (loan, insurance, SIP, tax saving)
7. ET products they've heard of

Keep responses concise (<80 words). Be warm, professional, not pushy.
When you have enough info (5+ answers), end with: "Great! I now have a good picture of your financial goals. Let me build your personalized profile."
"""

PROFILING_PROMPT_TEMPLATE = """Analyze this conversation and extract a structured user financial profile.
Return ONLY valid JSON — no markdown, no explanation, no code fences.

Conversation:
{conversation}

Required JSON format:
{{
  "persona": "one of: student | young_professional | mid_career | pre_retiree | retiree | business_owner",
  "risk_level": "one of: conservative | moderate | aggressive",
  "goals": ["list of financial goals mentioned"],
  "interests": ["list of financial topics/products they are interested in"],
  "recommended_products": ["list of ET products/services to recommend e.g. ET Money, ET Markets, SIP, Term Insurance, NPS"]
}}
"""

RECOMMENDATION_REASONING_PROMPT = """User profile:
{profile}

Recent behavior: {behavior}

Available products: {products}

Write a ONE-sentence compelling reason why each recommended product fits this user.
Return ONLY valid JSON in this format: {{"product_name": "reason"}}
No markdown, no explanation."""


# ──────────────────────────────────────────────────────────────────────────────
# GROQ — Conversational Chat
# ──────────────────────────────────────────────────────────────────────────────

def chat_with_groq(messages: list[dict]) -> str:
    """Send messages to Groq and return the assistant reply."""
    system = [{"role": "system", "content": CONCIERGE_SYSTEM_PROMPT}]
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=system + messages,
        max_tokens=512,
        temperature=0.7,
    )
    return response.choices[0].message.content


def stream_chat_groq(messages: list[dict]):
    """Generator that yields text chunks for SSE streaming."""
    system = [{"role": "system", "content": CONCIERGE_SYSTEM_PROMPT}]
    stream = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=system + messages,
        max_tokens=512,
        temperature=0.7,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


# ──────────────────────────────────────────────────────────────────────────────
# GROQ — Structured Profile Extraction
# ──────────────────────────────────────────────────────────────────────────────

def extract_profile_with_groq(conversation_text: str) -> dict:
    """
    Parse a full conversation into a structured user financial profile JSON.
    Uses a low-temperature Groq call to maximise JSON accuracy.
    """
    prompt = PROFILING_PROMPT_TEMPLATE.format(conversation=conversation_text)
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.1,   # low temp → more deterministic JSON output
    )
    raw = response.choices[0].message.content.strip()

    # Strip any accidental markdown fences
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    return json.loads(raw)


# Keep old name as an alias so chat.py doesn't need a change
extract_profile_with_gemini = extract_profile_with_groq


# ──────────────────────────────────────────────────────────────────────────────
# GROQ — Recommendation Reasoning
# ──────────────────────────────────────────────────────────────────────────────

def generate_recommendation_reasons(profile: dict, behavior: list, products: list) -> dict:
    """
    Generate a one-sentence reason for each recommended product.
    Returns {"product_name": "reason"} dict.
    """
    prompt = RECOMMENDATION_REASONING_PROMPT.format(
        profile=json.dumps(profile, indent=2),
        behavior=json.dumps(behavior, indent=2),
        products=json.dumps(products),
    )
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.3,
    )
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    try:
        return json.loads(raw)
    except Exception:
        return {}


# ──────────────────────────────────────────────────────────────────────────────
# GROQ — RAG Answer Generation
# ──────────────────────────────────────────────────────────────────────────────

def answer_with_context(user_question: str, context_chunks: list[str], user_profile: dict | None = None) -> str:
    """
    Generate a personalized RAG answer from retrieved context chunks.
    """
    context = "\n\n".join(context_chunks[:4])  # max 4 chunks for token efficiency
    profile_hint = ""
    if user_profile:
        profile_hint = (
            f"\nUser profile: {user_profile.get('persona','')}, "
            f"{user_profile.get('risk_level','')} risk, "
            f"goals: {user_profile.get('goals','')}"
        )

    system = (
        f"You are ET Financial Navigator, a knowledgeable financial assistant. "
        f"Answer using the provided context. Be concise (<150 words), practical, and personalized.{profile_hint} "
        f"If context is insufficient, say so honestly."
    )
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_question}"},
        ],
        max_tokens=400,
        temperature=0.5,
    )
    return response.choices[0].message.content
