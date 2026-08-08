import logging
from functools import lru_cache
from typing import List, Union
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

from backend.config.settings import get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Singleton service to generate vector embeddings using SentenceTransformers.
    Uses 'sentence-transformers/all-MiniLM-L6-v2' (384 dimensions).
    """

    def __init__(self, model_name: str = None):
        self.settings = get_settings()
        self.model_name = model_name or self.settings.EMBEDDING_MODEL_NAME
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """
        Loads the SentenceTransformer model into memory once.
        """
        if self.model is not None:
            return

        if SentenceTransformer is None:
            raise ImportError(
                "The 'sentence-transformers' package is required. "
                "Please install it via 'pip install sentence-transformers'."
            )

        try:
            logger.info(f"Loading SentenceTransformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("SentenceTransformer model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model '{self.model_name}': {e}")
            raise RuntimeError(f"Could not load embedding model: {e}") from e

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generates a 384-dimensional vector embedding for a single text string.

        Args:
            text (str): Input text query or review text.

        Returns:
            List[float]: Python list of floats representing the embedding vector.
        """
        if not text or not text.strip():
            # Return zero vector of length 384 for empty input
            return [0.0] * 384

        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generates vector embeddings for a list of text strings in batch.

        Args:
            texts (List[str]): List of input text strings.

        Returns:
            List[List[float]]: List of float embedding vectors.
        """
        if not texts:
            return []

        # Replace empty strings with a single space to prevent model encode errors
        cleaned_texts = [t if t and t.strip() else " " for t in texts]

        embeddings = self.model.encode(
            cleaned_texts,
            batch_size=32,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        return embeddings.tolist()


class ChromaEmbeddingFunction:
    """
    ChromaDB compatible embedding function adapter wrapper.
    Allows Chroma collection query methods to generate embeddings automatically.
    """

    def __init__(self, embedding_service: EmbeddingService = None):
        self.embedding_service = embedding_service or get_embedding_service()

    def __call__(self, input_texts: Union[str, List[str]]) -> List[List[float]]:
        if isinstance(input_texts, str):
            input_texts = [input_texts]
        return self.embedding_service.generate_embeddings_batch(input_texts)


@lru_cache()
def get_embedding_service() -> EmbeddingService:
    """
    Singleton accessor for the EmbeddingService instance.
    Loads the model only once and reuses it across requests.
    """
    return EmbeddingService()
