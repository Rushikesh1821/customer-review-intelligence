import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_INSTRUCTION = """You are an expert AI Customer Review Intelligence Analyst.
Your goal is to provide accurate, factual, and concise answers to user questions based strictly on the provided customer reviews.

Guidelines:
1. Base your answer ONLY on the provided customer reviews below. Do not invent or extrapolate outside information.
2. Be objective, professional, and clear.
3. Highlight key patterns, specific pros/cons, and customer sentiments when applicable.
4. If the provided customer reviews do not contain enough information to answer the question, clearly state: 'Based on the retrieved customer reviews, there is not enough information to answer this question.'
"""


class PromptBuilder:
    """
    Prompt Builder utility for RAG generation, product analytics summaries, and comparative analysis.
    """

    def __init__(self, system_instruction: Optional[str] = None):
        self.system_instruction = system_instruction or DEFAULT_SYSTEM_INSTRUCTION

    def format_reviews_context(self, reviews: List[Dict[str, Any]]) -> str:
        """
        Formats a list of retrieved review dictionaries into a clean, structured context text block.

        Args:
            reviews (List[Dict[str, Any]]): List of review objects containing 'text', 'product', 'rating', 'sentiment'.

        Returns:
            str: Formatted context block.
        """
        if not reviews:
            return "No relevant customer reviews found."

        context_blocks = []
        for idx, rev in enumerate(reviews, start=1):
            product = rev.get("product", "Unknown Product")
            rating = rev.get("rating", "N/A")
            sentiment = rev.get("sentiment", "N/A")
            text = rev.get("text", "").strip()

            block = (
                f"[Review #{idx}]\n"
                f"• Product: {product}\n"
                f"• Rating: {rating} / 5.0\n"
                f"• Sentiment: {sentiment}\n"
                f"• Customer Feedback: \"{text}\""
            )
            context_blocks.append(block)

        return "\n\n".join(context_blocks)

    def build_rag_prompt(self, question: str, retrieved_reviews: List[Dict[str, Any]]) -> str:
        """
        Builds a complete RAG prompt for answering a user question using retrieved customer reviews.

        Args:
            question (str): User's natural language question.
            retrieved_reviews (List[Dict[str, Any]]): List of retrieved review objects from vector search.

        Returns:
            str: Complete prompt string formatted for Gemini API.
        """
        context_str = self.format_reviews_context(retrieved_reviews)

        prompt = f"""{self.system_instruction}

Customer Reviews Context:
==================================================
{context_str}
==================================================

User Question:
{question}

Detailed Executive Answer:"""
        return prompt

    def build_product_summary_prompt(self, product_name: str, reviews: List[Dict[str, Any]]) -> str:
        """
        Builds a prompt to generate an AI summary of overall customer feedback for a specific product.

        Args:
            product_name (str): Product name.
            reviews (List[Dict[str, Any]]): Sample of customer reviews for this product.

        Returns:
            str: Product summary prompt string.
        """
        context_str = self.format_reviews_context(reviews)

        prompt = f"""You are an executive product intelligence analyst.

Analyze the customer reviews below for the product: "{product_name}".

Customer Reviews:
==================================================
{context_str}
==================================================

Provide a structured analysis covering:
1. Overall Sentiment Overview: Summary of overall customer sentiment and satisfaction level.
2. Top Strengths & Praise: What customers love most about this product.
3. Top Complaints & Issues: The most common customer complaints or flaws reported.
4. Final Verdict & Recommendation: Brief recommendation for potential buyers.
"""
        return prompt

    def build_product_comparison_prompt(
        self,
        product_a: str,
        reviews_a: List[Dict[str, Any]],
        product_b: str,
        reviews_b: List[Dict[str, Any]],
    ) -> str:
        """
        Builds a prompt to compare customer feedback between two products.
        """
        context_a = self.format_reviews_context(reviews_a)
        context_b = self.format_reviews_context(reviews_b)

        prompt = f"""You are a product intelligence comparative analyst.

Compare customer satisfaction and feedback for Product A vs Product B based ONLY on the customer reviews provided below.

Product A: "{product_a}"
Reviews for Product A:
--------------------------------------------------
{context_a}
--------------------------------------------------

Product B: "{product_b}"
Reviews for Product B:
--------------------------------------------------
{context_b}
--------------------------------------------------

Provide a head-to-head comparative report covering:
1. Key Advantages of Product A over Product B
2. Key Advantages of Product B over Product A
3. Common Pain Points for both products
4. Overall Winner & Best Use Cases for each product
"""
        return prompt


# Module-level default builder instance
_default_builder = PromptBuilder()


def build_rag_prompt(question: str, retrieved_reviews: List[Dict[str, Any]]) -> str:
    """
    Helper function to generate a standard RAG prompt.
    """
    return _default_builder.build_rag_prompt(question, retrieved_reviews)
