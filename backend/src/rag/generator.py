import os
import logging
from functools import lru_cache
from typing import Dict, List, Any, Optional

try:
    from google import genai
except ImportError:
    genai = None

from backend.config.settings import get_settings
from backend.src.rag.prompt_builder import PromptBuilder, build_rag_prompt

logger = logging.getLogger(__name__)


class GeminiGenerator:
    """
    Singleton Gemini API Generator for RAG Q&A, product analysis summaries,
    and review insight generation.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.settings = get_settings()
        self.api_key = api_key or self.settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.client = None
        self.prompt_builder = PromptBuilder()
        self._initialize_client()

    def _initialize_client(self) -> None:
        """
        Initializes the Gemini Client singleton instance.
        """
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not set. Gemini AI generation will operate in fallback mode.")
            return

        if genai is None:
            logger.error("The 'google-genai' package is not installed. Run 'pip install google-genai'.")
            return

        try:
            logger.info("Initializing Google Gemini API Client...")
            self.client = genai.Client(api_key=self.api_key)
            logger.info("Gemini API Client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API Client: {e}")

    def generate(self, prompt: str, model_name: Optional[str] = None) -> str:
        """
        Generates text response using Gemini API.

        Args:
            prompt (str): Prepared prompt string.
            model_name (str, optional): Target Gemini model name.

        Returns:
            str: Generated text answer.
        """
        if not prompt or not prompt.strip():
            return "Empty prompt provided."

        target_model = model_name or self.settings.GEMINI_MODEL or "gemini-2.5-flash"

        if not self.client:
            # Re-attempt client initialization in case API key was added dynamically
            self.api_key = self.settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
            if self.api_key and genai:
                try:
                    self.client = genai.Client(api_key=self.api_key)
                except Exception as e:
                    logger.error(f"Re-initialization failed: {e}")

        if not self.client:
            return (
                "Gemini API key is not configured. Please set the GEMINI_API_KEY environment variable "
                "to enable real-time Gemini AI review analysis."
            )

        fallback_models = [target_model, "gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]
        # Remove duplicates while preserving order
        unique_models = []
        for m in fallback_models:
            if m not in unique_models:
                unique_models.append(m)

        for current_model in unique_models:
            try:
                logger.info(f"Sending generation request to Gemini model '{current_model}'...")
                response = self.client.models.generate_content(
                    model=current_model,
                    contents=prompt,
                )
                if hasattr(response, "text") and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini API generation failed for model '{current_model}': {e}")
                continue

        return "Error generating answer using Gemini AI across available models."

    def answer_question(
        self,
        question: str,
        retrieved_reviews: List[Dict[str, Any]],
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes end-to-end RAG answer generation:
        1. Formats RAG prompt with retrieved customer reviews.
        2. Queries Gemini API for a grounded answer.
        3. Returns complete response object with retrieved review citations.

        Args:
            question (str): User question.
            retrieved_reviews (List[Dict[str, Any]]): Retrieved review objects from ChromaDB vector search.
            model_name (str, optional): Target Gemini model name.

        Returns:
            Dict[str, Any]: Answer object containing question, answer text, review citations, and metadata.
        """
        if not retrieved_reviews:
            return {
                "question": question,
                "answer": "No relevant customer reviews found matching your query to generate an answer.",
                "retrieved_reviews": [],
                "review_count": 0,
                "model_used": model_name or self.settings.GEMINI_MODEL,
            }

        prompt = self.prompt_builder.build_rag_prompt(question, retrieved_reviews)
        answer_text = self.generate(prompt=prompt, model_name=model_name)

        return {
            "question": question,
            "answer": answer_text,
            "retrieved_reviews": retrieved_reviews,
            "review_count": len(retrieved_reviews),
            "model_used": model_name or self.settings.GEMINI_MODEL,
        }

    def summarize_product(
        self,
        product_name: str,
        reviews: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Generates an AI product feedback summary for a given product.
        """
        prompt = self.prompt_builder.build_product_summary_prompt(product_name, reviews)
        summary_text = self.generate(prompt=prompt)
        return {
            "product_name": product_name,
            "summary": summary_text,
            "review_count": len(reviews),
        }


@lru_cache()
def get_gemini_generator() -> GeminiGenerator:
    """
    Singleton accessor function for GeminiGenerator instance.
    """
    return GeminiGenerator()
