from pathlib import Path
from typing import Any
import uuid

import chromadb
from sentence_transformers import SentenceTransformer


class MemoryStore:
    def __init__(
        self,
        db_path: str = "data/vector",
        collection_name: str = "conversation_memory",
        model_name: str = "all-MiniLM-L6-v2",
    ) -> None:
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=str(self.db_path))
        self.collection = self.client.get_or_create_collection(collection_name)
        self.embedder = SentenceTransformer(model_name)

    def add(
        self,
        text: str,
        memory_id: str | None = None,
        domain: str = "general",
    ) -> None:
        if len(text) > 1200:
            text = text[:1200]

        if memory_id is None:
            memory_id = str(uuid.uuid4())

        domain = (domain or "general").strip().lower()
        embedding = self.embedder.encode(text).tolist()

        self.collection.add(
            ids=[memory_id],
            documents=[text],
            embeddings=[embedding],
            metadatas=[{"domain": domain}],
        )

    def search(
        self,
        query: str,
        limit: int = 5,
        domain: str | None = None,
    ) -> list[str]:
        query_embedding = self.embedder.encode(query).tolist()

        query_args: dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": limit,
        }

        if domain:
            query_args["where"] = {"domain": domain.strip().lower()}

        results = self.collection.query(**query_args)

        documents = results.get("documents", [])
        if not documents:
            return []

        return documents[0]

    def get_recent(
        self,
        limit: int = 3,
        domain: str | None = None,
    ) -> list[str]:
        get_args: dict[str, Any] = {
            "include": ["documents", "metadatas"],
        }

        if domain:
            get_args["where"] = {"domain": domain.strip().lower()}

        results = self.collection.get(**get_args)

        documents = results.get("documents", [])
        if not documents:
            return []

        return documents[-limit:]

    def get_context(
        self,
        query: str,
        domain: str | None = None,
        recent_limit: int = 3,
        semantic_limit: int = 2,
        loose_limit: int = 1,
        max_total: int = 3,
    ) -> list[str]:
        recent_docs = self.get_recent(limit=recent_limit, domain=domain)
        semantic_docs = self.search(query=query, limit=semantic_limit, domain=domain)
        loose_docs = self.search(query=query, limit=loose_limit)

        combined: list[str] = []
        seen: set[str] = set()

        for group in (recent_docs, semantic_docs, loose_docs):
            for doc in group:
                if doc not in seen:
                    combined.append(doc)
                    seen.add(doc)
                if len(combined) >= max_total:
                    return combined

        return combined


memory_store = MemoryStore()