import logging
from functools import lru_cache
from typing import Dict, List, Optional, Any
import chromadb
from chromadb.config import Settings as ChromaSettings

from backend.config.settings import get_settings
from backend.src.rag.embeddings import get_embedding_service, EmbeddingService
from backend.src.rag.query_expansion import expand_query

logger = logging.getLogger(__name__)


class ReviewRetriever:
    """
    Singleton ChromaDB Vector DB Retriever for e-commerce customer reviews.
    Supports semantic vector search, query expansion, deduplication, and metadata filtering.
    """

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
    ):
        self.settings = get_settings()
        self.embedding_service = embedding_service or get_embedding_service()
        self.client = None
        self.collection = None
        self._is_loaded = False
        self._initialize_chroma()

    def _initialize_chroma(self) -> None:
        """
        Initializes the persistent ChromaDB client and loads the target collection once.
        """
        if self._is_loaded:
            return

        db_path = str(self.settings.CHROMA_DB_DIR)
        collection_name = self.settings.CHROMA_COLLECTION_NAME

        try:
            logger.info(f"Initializing Persistent ChromaDB client at: {db_path}")
            self.client = chromadb.PersistentClient(
                path=db_path,
                settings=ChromaSettings(anonymized_telemetry=False)
            )

            logger.info(f"Retrieving collection: '{collection_name}'")
            self.collection = self.client.get_collection(name=collection_name)
            self._is_loaded = True
            logger.info(f"Successfully loaded ChromaDB collection '{collection_name}' with {self.collection.count()} items.")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB collection '{collection_name}' at '{db_path}': {e}")
            raise RuntimeError(f"ChromaDB connection error: {e}") from e

    def _build_where_filter(
        self,
        product: Optional[str] = None,
        sentiment: Optional[str] = None,
        rating: Optional[float] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Constructs ChromaDB where clause dictionary based on provided filters.
        """
        conditions = []
        if product and product.strip() and product.lower() != "all":
            conditions.append({"product": product.strip()})
        if sentiment and sentiment.strip() and sentiment.lower() != "all":
            conditions.append({"sentiment": sentiment.strip().capitalize()})
        if rating is not None and rating > 0:
            conditions.append({"rating": float(rating)})

        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return {"$and": conditions}

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        product: Optional[str] = None,
        sentiment: Optional[str] = None,
        rating: Optional[float] = None,
        enable_query_expansion: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Performs semantic vector search over customer reviews using ChromaDB.

        Args:
            query (str): Natural language user search prompt or question.
            top_k (int): Number of top relevant reviews to retrieve.
            product (str, optional): Product name filter.
            sentiment (str, optional): Sentiment filter ('Positive', 'Neutral', 'Negative').
            rating (float, optional): Exact rating filter.
            enable_query_expansion (bool): Whether to expand query with domain synonyms.

        Returns:
            List[Dict[str, Any]]: List of retrieved review objects with metadata & similarity scores.
        """
        if not query or not query.strip():
            return []

        k = top_k or self.settings.RAG_TOP_K

        # Step 1: Query Expansion (optional)
        search_query = expand_query(query) if enable_query_expansion else query.strip()
        logger.debug(f"Retriever search query: '{search_query}' (Original: '{query}')")

        # Step 2: Generate Query Embedding
        query_vector = self.embedding_service.generate_embedding(search_query)

        # Step 3: Build Metadata Filter
        where_filter = self._build_where_filter(product=product, sentiment=sentiment, rating=rating)

        # Fetch extra results to allow post-retrieval deduplication
        fetch_limit = min(k * 3, 50)

        try:
            query_kwargs = {
                "query_embeddings": [query_vector],
                "n_results": fetch_limit,
            }
            if where_filter:
                query_kwargs["where"] = where_filter

            results = self.collection.query(**query_kwargs)
        except Exception as e:
            logger.error(f"Error executing ChromaDB query: {e}")
            return []

        if not results or not results.get("documents") or not results["documents"][0]:
            return []

        docs = results["documents"][0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        retrieved_reviews: List[Dict[str, Any]] = []
        seen_texts = set()

        for idx in range(len(docs)):
            doc_text = docs[idx]
            meta = metadatas[idx] if idx < len(metadatas) else {}
            dist = distances[idx] if idx < len(distances) else 0.0
            doc_id = ids[idx] if idx < len(ids) else f"review_{idx}"

            # Step 4: Duplicate Removal
            text_normalized = doc_text.strip().lower()
            if text_normalized in seen_texts:
                continue
            seen_texts.add(text_normalized)

            # Convert distance to similarity score (Chroma uses L2 distance or cosine distance)
            similarity_score = round(max(0.0, 1.0 - (dist / 2.0)), 4) if dist is not None else 1.0

            retrieved_reviews.append({
                "id": doc_id,
                "text": doc_text,
                "product": meta.get("product", "Unknown Product"),
                "rating": meta.get("rating", 0.0),
                "sentiment": meta.get("sentiment", "Neutral"),
                "distance": round(float(dist), 4) if dist is not None else 0.0,
                "similarity_score": similarity_score,
            })

            if len(retrieved_reviews) >= k:
                break

        return retrieved_reviews


@lru_cache()
def get_review_retriever() -> ReviewRetriever:
    """
    Singleton accessor function for ReviewRetriever instance.
    Ensures ChromaDB client and embeddings service are loaded only once.
    """
    return ReviewRetriever()
