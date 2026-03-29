"""
RAG Service — Retrieval-Augmented Generation Pipeline

Flow:
1. Embed user query using sentence-transformers (local, no API cost)
2. Search Weaviate FinancialContent + ETProduct collections with near_vector
3. Return top-k text chunks to be used as context in LLM prompt
"""
from sentence_transformers import SentenceTransformer
from db.weaviate_client import get_client
import weaviate.classes as wvc

# Load embedding model once at module level (cached on disk after first download)
_embedder: SentenceTransformer | None = None


def get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        # all-MiniLM-L6-v2: 80MB, fast, great for sentence similarity
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


def embed_text(text: str) -> list[float]:
    """Return a normalized embedding vector for the given text."""
    return get_embedder().encode(text, normalize_embeddings=True).tolist()


def add_financial_content(title: str, content: str, category: str, tags: str = "") -> str:
    """
    Insert a content item into Weaviate FinancialContent with its vector.
    Returns the Weaviate UUID.
    """
    client = get_client()
    collection = client.collections.get("FinancialContent")
    vector = embed_text(f"{title} {content}")
    uid = collection.data.insert(
        properties={
            "title": title,
            "content": content,
            "category": category,
            "tags": tags,
        },
        vector=vector,
    )
    return str(uid)


def add_et_product(name: str, category: str, description: str, target_persona: str, risk_level: str, url: str = "") -> str:
    """Insert an ET product into Weaviate ETProduct collection."""
    client = get_client()
    collection = client.collections.get("ETProduct")
    vector = embed_text(f"{name} {description} {category} {target_persona}")
    uid = collection.data.insert(
        properties={
            "name": name,
            "category": category,
            "description": description,
            "target_persona": target_persona,
            "risk_level": risk_level,
            "url": url,
        },
        vector=vector,
    )
    return str(uid)


def semantic_search(query: str, collection_name: str, limit: int = 4) -> list[dict]:
    """
    Search a Weaviate collection using near_vector similarity.
    Returns a list of property dicts for top-k results.
    """
    client = get_client()
    collection = client.collections.get(collection_name)
    vector = embed_text(query)

    results = collection.query.near_vector(
        near_vector=vector,
        limit=limit,
        return_properties=True,
    )
    return [obj.properties for obj in results.objects]


def retrieve_context_for_query(query: str) -> list[str]:
    """
    Retrieve relevant text chunks from both FinancialContent and ETProduct
    for use as RAG context. Returns a list of plain text strings.
    """
    content_hits = semantic_search(query, "FinancialContent", limit=3)
    product_hits = semantic_search(query, "ETProduct", limit=2)

    chunks = []
    for item in content_hits:
        chunks.append(f"[Article: {item.get('title','')}]\n{item.get('content','')}")
    for item in product_hits:
        chunks.append(f"[Product: {item.get('name','')}]\n{item.get('description','')}")

    return chunks
