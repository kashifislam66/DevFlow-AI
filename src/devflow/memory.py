import os
import uuid
import chromadb
from chromadb.config import Settings

# Persistent storage under the project data directory.
CHROMA_PATH = os.path.join(os.getcwd(), "data", "chroma_db")
print(f"Chroma DB path: {CHROMA_PATH}")
COLLECTION_NAME = "devflow_memory"


def get_chroma_collection():
    """Persistent Chroma client + collection."""
    os.makedirs(CHROMA_PATH, exist_ok=True)

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "DevFlow project memory"},
    )
    return collection


def store_memory(text: str, metadata: dict | None = None) -> str:
    """Store a text memory with optional metadata."""
    if not text or not text.strip():
        return "Skipped: empty text"

    collection = get_chroma_collection()
    doc_id = str(uuid.uuid4())

    meta = metadata or {}
    # Chroma metadata values should be str/int/float/bool
    clean_meta = {k: (v if isinstance(v, (str, int, float, bool)) else str(v)) for k, v in meta.items()}

    collection.add(
        documents=[text.strip()],
        metadatas=[clean_meta],
        ids=[doc_id],
    )
    return f"Stored memory id={doc_id}"


def search_memory(query: str, n_results: int = 3) -> str:
    """Semantic search over stored memories."""
    if not query or not query.strip():
        return "No query provided."

    collection = get_chroma_collection()

    count = collection.count()
    if count == 0:
        return "No memories stored yet."

    n = min(n_results, count)
    results = collection.query(
        query_texts=[query],
        n_results=n,
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]

    if not docs:
        return "No relevant memories found."

    chunks = []
    for i, doc in enumerate(docs):
        meta = metas[i] if i < len(metas) else {}
        chunks.append(f"[{i+1}] {doc[:800]}\n  meta: {meta}")

    return "\n\n".join(chunks)
