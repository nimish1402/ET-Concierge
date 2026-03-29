"""
Weaviate Client + Schema Initialization

All data (Users, Events, Recommendations, FinancialContent, ETProducts)
is stored in Weaviate. Structured objects use `none` vectorizer to skip
auto-vectorization; content collections supply their own vectors for similarity search.

Supports:
  - Weaviate Cloud (WCS): set WEAVIATE_URL=<cluster-url> and WEAVIATE_API_KEY=<key>
  - Local Docker:          set WEAVIATE_URL=http://localhost:8080, leave WEAVIATE_API_KEY blank
"""
import weaviate
import weaviate.auth as weaviate_auth
from weaviate.classes.config import Configure, Property, DataType
from config import settings

# Module-level singleton client
_client: weaviate.WeaviateClient | None = None


def _is_connected(client: weaviate.WeaviateClient) -> bool:
    try:
        return client.is_connected()
    except Exception:
        return False


def get_client() -> weaviate.WeaviateClient:
    """Return the global Weaviate client, creating it if needed."""
    global _client
    if _client is None or not _is_connected(_client):
        if settings.WEAVIATE_API_KEY:
            # Weaviate Cloud Services (WCS) — connect_to_wcs is the v4 function name
            _client = weaviate.connect_to_wcs(
                cluster_url=settings.WEAVIATE_URL,
                auth_credentials=weaviate_auth.AuthApiKey(settings.WEAVIATE_API_KEY),
            )
        else:
            # Local Docker Weaviate
            url = settings.WEAVIATE_URL.replace("http://", "").replace("https://", "")
            host = url.split(":")[0]
            port = int(url.split(":")[1]) if ":" in url else 8080
            _client = weaviate.connect_to_local(host=host, port=port)
    return _client


def _collection_exists(client: weaviate.WeaviateClient, name: str) -> bool:
    return client.collections.exists(name)


def init_weaviate_schema():
    """Create all required Weaviate collections if they don't exist."""
    client = get_client()

    # ── Users ─────────────────────────────────────────────────────────────────
    if not _collection_exists(client, "User"):
        client.collections.create(
            name="User",
            description="Stores user profiles built from onboarding conversations",
            vectorizer_config=Configure.Vectorizer.none(),
            properties=[
                Property(name="name", data_type=DataType.TEXT),
                Property(name="persona", data_type=DataType.TEXT),
                Property(name="risk_level", data_type=DataType.TEXT),
                Property(name="goals", data_type=DataType.TEXT),        # JSON string
                Property(name="interests", data_type=DataType.TEXT),    # JSON string
                Property(name="recommended_products", data_type=DataType.TEXT),  # JSON string
                Property(name="created_at", data_type=DataType.TEXT),
            ],
        )

    # ── Events ────────────────────────────────────────────────────────────────
    if not _collection_exists(client, "Event"):
        client.collections.create(
            name="Event",
            description="Tracks user behavior events for recommendation scoring",
            vectorizer_config=Configure.Vectorizer.none(),
            properties=[
                Property(name="user_id", data_type=DataType.TEXT),
                Property(name="event_type", data_type=DataType.TEXT),  # click, search, view
                Property(name="metadata", data_type=DataType.TEXT),    # JSON string
                Property(name="timestamp", data_type=DataType.TEXT),
            ],
        )

    # ── Recommendations ───────────────────────────────────────────────────────
    if not _collection_exists(client, "Recommendation"):
        client.collections.create(
            name="Recommendation",
            description="Stores generated product recommendations per user",
            vectorizer_config=Configure.Vectorizer.none(),
            properties=[
                Property(name="user_id", data_type=DataType.TEXT),
                Property(name="product", data_type=DataType.TEXT),
                Property(name="reason", data_type=DataType.TEXT),
                Property(name="score", data_type=DataType.NUMBER),
                Property(name="created_at", data_type=DataType.TEXT),
            ],
        )

    # ── FinancialContent ──────────────────────────────────────────────────────
    if not _collection_exists(client, "FinancialContent"):
        client.collections.create(
            name="FinancialContent",
            description="Articles, guides, and FAQs for RAG retrieval",
            vectorizer_config=Configure.Vectorizer.none(),  # We supply our own vectors
            properties=[
                Property(name="title", data_type=DataType.TEXT),
                Property(name="content", data_type=DataType.TEXT),
                Property(name="category", data_type=DataType.TEXT),  # e.g. mutual_funds, stocks
                Property(name="tags", data_type=DataType.TEXT),      # CSV tags
            ],
        )

    # ── ETProducts ────────────────────────────────────────────────────────────
    if not _collection_exists(client, "ETProduct"):
        client.collections.create(
            name="ETProduct",
            description="ET ecosystem financial products: credit cards, loans, insurance, etc.",
            vectorizer_config=Configure.Vectorizer.none(),
            properties=[
                Property(name="name", data_type=DataType.TEXT),
                Property(name="category", data_type=DataType.TEXT),
                Property(name="description", data_type=DataType.TEXT),
                Property(name="target_persona", data_type=DataType.TEXT),   # CSV personas
                Property(name="risk_level", data_type=DataType.TEXT),
                Property(name="url", data_type=DataType.TEXT),
            ],
        )

    print("✅ Weaviate schema initialized")
