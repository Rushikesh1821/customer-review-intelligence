import logging
from functools import lru_cache
from typing import Dict, List, Any, Optional

from backend.src.sentiment.sentiment_predictor import get_sentiment_predictor, SentimentPredictor
from backend.src.rag.retriever import get_review_retriever, ReviewRetriever
from backend.src.rag.generator import get_gemini_generator, GeminiGenerator
from backend.src.analytics.analytics import get_analytics_service, AnalyticsService

logger = logging.getLogger(__name__)


class ReviewService:
    """
    Unified Orchestration Service for the Customer Review Intelligence Platform.
    Integrates Sentiment Analysis, RAG Vector Retrieval, Gemini Generation, and Data Analytics.
    """

    def __init__(
        self,
        sentiment_predictor: Optional[SentimentPredictor] = None,
        retriever: Optional[ReviewRetriever] = None,
        generator: Optional[GeminiGenerator] = None,
        analytics: Optional[AnalyticsService] = None,
    ):
        # Dependencies are initialized lazily. This keeps lightweight analytics endpoints
        # responsive without requiring the sentence-transformer or sentiment model first.
        self.sentiment_predictor = sentiment_predictor
        self.retriever = retriever
        self.generator = generator
        self.analytics = analytics

    def _get_sentiment_predictor(self) -> SentimentPredictor:
        if self.sentiment_predictor is None:
            self.sentiment_predictor = get_sentiment_predictor()
        return self.sentiment_predictor

    def _get_retriever(self) -> ReviewRetriever:
        if self.retriever is None:
            self.retriever = get_review_retriever()
        return self.retriever

    def _get_generator(self) -> GeminiGenerator:
        if self.generator is None:
            self.generator = get_gemini_generator()
        return self.generator

    def _get_analytics(self) -> AnalyticsService:
        if self.analytics is None:
            self.analytics = get_analytics_service()
        return self.analytics

    def predict_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Predicts sentiment classification and class probabilities for a review string.
        """
        if not text or not text.strip():
            return {
                "sentiment": "Neutral",
                "confidence": 0.5,
                "probabilities": {"Negative": 0.33, "Neutral": 0.34, "Positive": 0.33},
                "preprocessed_text": "",
            }
        return self._get_sentiment_predictor().predict(text)

    def ask_ai(
        self,
        question: str,
        product: Optional[str] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Answers a user question using RAG:
        1. Expands search query and queries ChromaDB vector store.
        2. Formats retrieved review context with metadata.
        3. Calls Gemini AI for a grounded factual answer.
        """
        if not question or not question.strip():
            return {
                "question": "",
                "answer": "Please enter a valid question.",
                "retrieved_reviews": [],
                "review_count": 0,
                "model_used": self._get_generator().settings.GEMINI_MODEL,
            }

        # Step 1: Vector Retrieval from ChromaDB
        retrieved_reviews = self._get_retriever().retrieve(
            query=question,
            top_k=top_k,
            product=product,
            enable_query_expansion=True,
        )

        # Step 2: Gemini Generation
        rag_response = self._get_generator().answer_question(
            question=question,
            retrieved_reviews=retrieved_reviews,
        )

        return rag_response

    def get_dashboard(self) -> Dict[str, Any]:
        """
        Returns executive dashboard analytical stats and charts data.
        """
        return self._get_analytics().get_dashboard_analytics()

    def get_products(self, search: str = "", limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Returns list of available products with review counts and average ratings.
        """
        return self._get_analytics().get_products(search=search, limit=limit, offset=offset)

    def get_product_by_name(self, product_name: str) -> Dict[str, Any]:
        """
        Returns detailed product analytics, sentiment breakdown, complaints, and AI summary.
        """
        return self._get_analytics().get_product_analytics(product_name=product_name)

    def explore_reviews(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str = "",
        product: str = "",
        sentiment: str = "",
        rating: Optional[float] = None,
        is_semantic: bool = False,
    ) -> Dict[str, Any]:
        """
        Explores reviews using either standard tabular filters or semantic vector search.
        """
        if is_semantic and search and search.strip():
            # Use ChromaDB vector retrieval for semantic search
            results = self._get_retriever().retrieve(
                query=search,
                top_k=page_size,
                product=product,
                sentiment=sentiment,
                rating=rating,
                enable_query_expansion=True,
            )
            return {
                "reviews": results,
                "total": len(results),
                "page": 1,
                "page_size": page_size,
                "total_pages": 1,
                "is_semantic": True,
            }

        # Standard keyword & tabular filtering
        return self._get_analytics().get_reviews_explorer(
            page=page,
            page_size=page_size,
            search=search,
            product=product,
            sentiment=sentiment,
            rating=rating,
        )

    def compare_products(self, product_a: str, product_b: str) -> Dict[str, Any]:
        """
        Compares customer intelligence metrics and AI insights between two products.
        """
        analytics = self._get_analytics()
        stats_a = analytics.get_product_analytics(product_a)
        stats_b = analytics.get_product_analytics(product_b)

        if "error" in stats_a:
            raise ValueError(stats_a["error"])
        if "error" in stats_b:
            raise ValueError(stats_b["error"])

        # Retrieve top review samples for comparative Gemini prompt
        retriever = self._get_retriever()
        generator = self._get_generator()
        sample_a = retriever.retrieve(query=product_a, top_k=5, product=product_a)
        sample_b = retriever.retrieve(query=product_b, top_k=5, product=product_b)

        prompt = generator.prompt_builder.build_product_comparison_prompt(
            product_a=product_a,
            reviews_a=sample_a,
            product_b=product_b,
            reviews_b=sample_b,
        )
        ai_comparison = generator.generate(prompt=prompt)

        return {
            "product_a": stats_a,
            "product_b": stats_b,
            "ai_comparison": ai_comparison,
        }


@lru_cache()
def get_review_service() -> ReviewService:
    """
    Singleton accessor function for ReviewService instance.
    """
    return ReviewService()
