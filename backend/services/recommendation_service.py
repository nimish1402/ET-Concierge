"""
Recommendation Engine — Rule-Based Scoring

Score formula:
    score = interest_weight (0-40) + behavior_weight (0-40) + recency_weight (0-20)

interest_weight: how well user interests match product tags
behavior_weight: how often user has clicked/viewed related products
recency_weight: decays for older events (recent = more weight)
"""
import json
from datetime import datetime, timezone
import weaviate.classes as wvc
from db.weaviate_client import get_client


# ── Static product catalog (supplemented by Weaviate ETProduct collection) ──
ET_PRODUCT_CATALOG = [
    {
        "product": "ET Money - SIP Investments",
        "category": "mutual_funds",
        "target_personas": ["young_professional", "mid_career", "student"],
        "risk_levels": ["moderate", "aggressive"],
        "interest_tags": ["sip", "mutual funds", "wealth", "investment"],
        "url": "https://www.etmoney.com",
    },
    {
        "product": "ET Markets - Stock Portfolio Tracker",
        "category": "stocks",
        "target_personas": ["young_professional", "mid_career", "business_owner"],
        "risk_levels": ["moderate", "aggressive"],
        "interest_tags": ["stocks", "equity", "market", "trading"],
        "url": "https://markets.economictimes.com",
    },
    {
        "product": "ET Money Tax Saver ELSS",
        "category": "tax_saving",
        "target_personas": ["young_professional", "mid_career"],
        "risk_levels": ["moderate", "aggressive"],
        "interest_tags": ["tax", "elss", "80c", "tax saving"],
        "url": "https://www.etmoney.com/tax-saving",
    },
    {
        "product": "Term Life Insurance Plan",
        "category": "insurance",
        "target_personas": ["mid_career", "young_professional", "pre_retiree"],
        "risk_levels": ["conservative", "moderate"],
        "interest_tags": ["insurance", "life cover", "protection", "family"],
        "url": "https://www.etmoney.com/insurance",
    },
    {
        "product": "Fixed Deposit - High Yield FD",
        "category": "fixed_income",
        "target_personas": ["pre_retiree", "retiree", "conservative"],
        "risk_levels": ["conservative"],
        "interest_tags": ["fd", "fixed deposit", "safe", "guaranteed returns"],
        "url": "https://economictimes.indiatimes.com",
    },
    {
        "product": "Personal Loan - Quick Approval",
        "category": "loans",
        "target_personas": ["young_professional", "mid_career", "business_owner"],
        "risk_levels": ["moderate", "aggressive"],
        "interest_tags": ["loan", "credit", "personal loan", "emi"],
        "url": "https://economictimes.indiatimes.com/wealth/borrow",
    },
    {
        "product": "Credit Card - ET Rewards Card",
        "category": "credit_card",
        "target_personas": ["young_professional", "mid_career", "business_owner"],
        "risk_levels": ["moderate", "aggressive"],
        "interest_tags": ["credit card", "rewards", "cashback", "lifestyle"],
        "url": "https://economictimes.indiatimes.com/wealth/spend",
    },
    {
        "product": "Gold Investment - Digital Gold",
        "category": "gold",
        "target_personas": ["mid_career", "pre_retiree", "retiree"],
        "risk_levels": ["conservative", "moderate"],
        "interest_tags": ["gold", "digital gold", "safe haven", "hedge"],
        "url": "https://www.etmoney.com/digital-gold",
    },
    {
        "product": "ET Money - NPS (National Pension System)",
        "category": "retirement",
        "target_personas": ["mid_career", "pre_retiree"],
        "risk_levels": ["conservative", "moderate"],
        "interest_tags": ["retirement", "nps", "pension", "long term"],
        "url": "https://www.etmoney.com/nps",
    },
]


def _interest_weight(product: dict, user_interests: list[str]) -> float:
    """
    Score how well a product's tags match user interests.
    Max: 40 points.
    """
    tags = set(t.lower() for t in product["interest_tags"])
    interests = set(i.lower() for i in user_interests)
    overlap = len(tags & interests)
    return min(overlap / max(len(tags), 1) * 40, 40)


def _persona_risk_weight(product: dict, persona: str, risk_level: str) -> float:
    """
    Bonus score for matching persona and risk level.
    Max: 30 points.
    """
    score = 0.0
    if persona in product["target_personas"]:
        score += 20
    if risk_level in product["risk_levels"]:
        score += 10
    return score


def _behavior_weight(product: dict, events: list[dict]) -> float:
    """
    Score based on user click/search/view events related to this product category.
    Max: 30 points.
    """
    category = product["category"]
    score = 0.0
    for event in events:
        meta = event.get("metadata", {})
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except Exception:
                meta = {}
        if meta.get("category") == category or category in str(meta).lower():
            event_type = event.get("event_type", "")
            if event_type == "click":
                score += 5
            elif event_type == "search":
                score += 7
            elif event_type == "view":
                score += 3
    return min(score, 30)


def get_user_events(user_id: str) -> list[dict]:
    """Fetch all events for a user from Weaviate."""
    client = get_client()
    collection = client.collections.get("Event")
    results = collection.query.fetch_objects(
        filters=wvc.query.Filter.by_property("user_id").equal(user_id),
        limit=50,
    )
    return [obj.properties for obj in results.objects]


def score_products(profile: dict, events: list[dict]) -> list[dict]:
    """
    Score all catalog products for a user and return sorted recommendations.
    """
    persona = profile.get("persona", "")
    risk_level = profile.get("risk_level", "moderate")
    interests = profile.get("interests", [])

    scored = []
    for product in ET_PRODUCT_CATALOG:
        score = (
            _interest_weight(product, interests)
            + _persona_risk_weight(product, persona, risk_level)
            + _behavior_weight(product, events)
        )
        scored.append({
            "product": product["product"],
            "category": product["category"],
            "url": product["url"],
            "score": round(score, 2),
            "reason": "",  # filled by LLM reasoning step
        })

    # Sort descending by score, return top 5
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:5]


def save_recommendations(user_id: str, recommendations: list[dict]):
    """Persist recommendation list to Weaviate."""
    client = get_client()
    collection = client.collections.get("Recommendation")
    now = datetime.now(timezone.utc).isoformat()
    for rec in recommendations:
        collection.data.insert({
            "user_id": user_id,
            "product": rec["product"],
            "reason": rec.get("reason", ""),
            "score": rec["score"],
            "created_at": now,
        })


def get_recommendations(user_id: str) -> list[dict]:
    """Retrieve saved recommendations for a user."""
    client = get_client()
    collection = client.collections.get("Recommendation")
    results = collection.query.fetch_objects(
        filters=wvc.query.Filter.by_property("user_id").equal(user_id),
        limit=10,
    )
    recs = [obj.properties for obj in results.objects]
    recs.sort(key=lambda x: x.get("score", 0), reverse=True)
    return recs
