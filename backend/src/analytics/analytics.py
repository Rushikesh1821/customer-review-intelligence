import os
import logging
from functools import lru_cache
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from backend.config.settings import get_settings
from backend.src.rag.generator import get_gemini_generator

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Singleton Analytics Service for computing dashboard metrics, rating distributions,
    product analytics, top complaints/positives, and paginated review exploration.
    """

    def __init__(self):
        self.settings = get_settings()
        self.df: Optional[pd.DataFrame] = None
        self.gemini_generator = get_gemini_generator()
        self._is_loaded = False
        self._load_data()

    def _load_data(self) -> None:
        """
        Loads the preprocessed customer reviews dataset into memory once.
        """
        if self._is_loaded:
            return

        # Attempt to load cleaned_reviews.csv from data directory
        possible_paths = [
            self.settings.SENTIMENT_MODEL_PATH.parent.parent / "data" / "processed" / "cleaned_reviews.csv",
            self.settings.SENTIMENT_MODEL_PATH.parent.parent.parent / "data" / "processed" / "cleaned_reviews.csv",
        ]

        csv_path = None
        for p in possible_paths:
            if p.exists():
                csv_path = p
                break

        if not csv_path or not csv_path.exists():
            logger.warning("cleaned_reviews.csv not found. Operating with fallback empty DataFrame.")
            self.df = pd.DataFrame(columns=["Product_name", "Price", "Rate", "Review", "Summary", "full_review", "sentiment"])
            self._is_loaded = True
            return

        try:
            logger.info(f"Loading analytics dataset from {csv_path}...")
            df = pd.read_csv(csv_path)

            # Ensure expected column names are standardized
            if "Product_name" not in df.columns and "product" in df.columns:
                df["Product_name"] = df["product"]
            if "Rate" not in df.columns and "rating" in df.columns:
                df["Rate"] = df["rating"]
            if "full_review" not in df.columns and "Review" in df.columns:
                df["full_review"] = df["Review"]

            df["Rate"] = pd.to_numeric(df["Rate"], errors="coerce").fillna(3.0)
            df["sentiment"] = df["sentiment"].astype(str).str.capitalize()
            df["Product_name"] = df["Product_name"].astype(str).str.strip()

            self.df = df
            self._is_loaded = True
            logger.info(f"Analytics dataset loaded successfully with {len(self.df)} records.")
        except Exception as e:
            logger.error(f"Failed to load analytics dataset: {e}")
            self.df = pd.DataFrame(columns=["Product_name", "Price", "Rate", "Review", "Summary", "full_review", "sentiment"])
            self._is_loaded = True

    def get_dashboard_analytics(self) -> Dict[str, Any]:
        """
        Calculates high-level metrics for the executive dashboard:
        Total Reviews, Products, Avg Rating, Sentiment % Breakdown, Rating Distribution.
        """
        if self.df is None or self.df.empty:
            return {
                "total_reviews": 0,
                "total_products": 0,
                "average_rating": 0.0,
                "positive_percentage": 0.0,
                "neutral_percentage": 0.0,
                "negative_percentage": 0.0,
                "sentiment_distribution": {"Positive": 0, "Neutral": 0, "Negative": 0},
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                "recent_reviews": [],
                "top_products": [],
            }

        total_reviews = int(len(self.df))
        total_products = int(self.df["Product_name"].nunique())
        average_rating = round(float(self.df["Rate"].mean()), 2)

        # Sentiment Distribution
        sentiment_counts = self.df["sentiment"].value_counts().to_dict()
        pos_count = int(sentiment_counts.get("Positive", 0))
        neu_count = int(sentiment_counts.get("Neutral", 0))
        neg_count = int(sentiment_counts.get("Negative", 0))

        pos_pct = round((pos_count / total_reviews) * 100, 2) if total_reviews > 0 else 0.0
        neu_pct = round((neu_count / total_reviews) * 100, 2) if total_reviews > 0 else 0.0
        neg_pct = round((neg_count / total_reviews) * 100, 2) if total_reviews > 0 else 0.0

        # Rating Distribution
        rating_counts = self.df["Rate"].value_counts().to_dict()
        rating_dist = {
            star: int(rating_counts.get(float(star), rating_counts.get(int(star), 0)))
            for star in range(1, 6)
        }

        # Top Reviewed Products
        top_prod_series = self.df.groupby("Product_name").agg(
            review_count=("Rate", "count"),
            avg_rating=("Rate", "mean")
        ).reset_index().sort_values(by="review_count", ascending=False).head(10)

        top_products = [
            {
                "product_name": row["Product_name"],
                "review_count": int(row["review_count"]),
                "avg_rating": round(float(row["avg_rating"]), 2),
            }
            for _, row in top_prod_series.iterrows()
        ]

        # Sample recent reviews
        sample_df = self.df.sample(min(6, total_reviews), random_state=42)
        recent_reviews = [
            {
                "id": str(idx),
                "product": str(row.get("Product_name", "")),
                "rating": float(row.get("Rate", 0.0)),
                "sentiment": str(row.get("sentiment", "Neutral")),
                "text": str(row.get("full_review", row.get("Review", ""))),
            }
            for idx, row in sample_df.iterrows()
        ]

        return {
            "total_reviews": total_reviews,
            "total_products": total_products,
            "average_rating": average_rating,
            "positive_percentage": pos_pct,
            "neutral_percentage": neu_pct,
            "negative_percentage": neg_pct,
            "sentiment_distribution": {
                "Positive": pos_count,
                "Neutral": neu_count,
                "Negative": neg_count,
            },
            "rating_distribution": rating_dist,
            "top_products": top_products,
            "recent_reviews": recent_reviews,
        }

    def get_products(self, search: str = "", limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Returns a list of unique products with aggregate review counts and ratings.
        """
        if self.df is None or self.df.empty:
            return {"products": [], "total_count": 0}

        agg_df = self.df.groupby("Product_name").agg(
            review_count=("Rate", "count"),
            avg_rating=("Rate", "mean")
        ).reset_index()

        if search and search.strip():
            query_lower = search.lower().strip()
            agg_df = agg_df[
                agg_df["Product_name"].str.lower().str.contains(
                    query_lower,
                    regex=False,
                    na=False,
                )
            ]

        total_count = int(len(agg_df))
        agg_df = agg_df.sort_values(by="review_count", ascending=False).iloc[offset : offset + limit]

        products = [
            {
                "product_name": row["Product_name"],
                "review_count": int(row["review_count"]),
                "avg_rating": round(float(row["avg_rating"]), 2),
            }
            for _, row in agg_df.iterrows()
        ]

        return {"products": products, "total_count": total_count}

    def get_product_analytics(self, product_name: str) -> Dict[str, Any]:
        """
        Calculates detailed statistics, sentiment breakdown, top complaints,
        top praise points, and AI summary for a specific product.
        """
        if self.df is None or self.df.empty:
            return {"error": "Dataset unavailable"}

        filtered_df = self.df[self.df["Product_name"].str.lower() == product_name.lower().strip()]
        if filtered_df.empty:
            # Partial substring match fallback
            filtered_df = self.df[self.df["Product_name"].str.lower().str.contains(product_name.lower().strip(), regex=False)]

        if filtered_df.empty:
            return {"error": f"Product '{product_name}' not found."}

        matched_product_name = str(filtered_df.iloc[0]["Product_name"])
        total_reviews = int(len(filtered_df))
        avg_rating = round(float(filtered_df["Rate"].mean()), 2)

        # Sentiment breakdown
        sentiment_counts = filtered_df["sentiment"].value_counts().to_dict()
        pos_count = int(sentiment_counts.get("Positive", 0))
        neu_count = int(sentiment_counts.get("Neutral", 0))
        neg_count = int(sentiment_counts.get("Negative", 0))

        pos_pct = round((pos_count / total_reviews) * 100, 2)
        neu_pct = round((neu_count / total_reviews) * 100, 2)
        neg_pct = round((neg_count / total_reviews) * 100, 2)

        # Rating distribution
        rating_counts = filtered_df["Rate"].value_counts().to_dict()
        rating_dist = {
            star: int(rating_counts.get(float(star), rating_counts.get(int(star), 0)))
            for star in range(1, 6)
        }

        # Top Complaints (Lowest rating / Negative sentiment sample)
        complaints_df = filtered_df[
            (filtered_df["sentiment"] == "Negative") | (filtered_df["Rate"] <= 2)
        ].head(5)
        top_complaints = [
            {
                "id": str(idx),
                "rating": float(row.get("Rate", 1.0)),
                "text": str(row.get("full_review", row.get("Review", ""))),
            }
            for idx, row in complaints_df.iterrows()
        ]

        # Top Positive Reviews (Highest rating / Positive sentiment sample)
        positives_df = filtered_df[
            (filtered_df["sentiment"] == "Positive") & (filtered_df["Rate"] >= 4)
        ].head(5)
        top_positives = [
            {
                "id": str(idx),
                "rating": float(row.get("Rate", 5.0)),
                "text": str(row.get("full_review", row.get("Review", ""))),
            }
            for idx, row in positives_df.iterrows()
        ]

        # Prepare AI Summary sample context
        sample_reviews = [
            {
                "product": matched_product_name,
                "rating": float(row.get("Rate", 3.0)),
                "sentiment": str(row.get("sentiment", "Neutral")),
                "text": str(row.get("full_review", row.get("Review", ""))),
            }
            for _, row in filtered_df.head(10).iterrows()
        ]

        summary_res = self.gemini_generator.summarize_product(matched_product_name, sample_reviews)

        return {
            "product_name": matched_product_name,
            "total_reviews": total_reviews,
            "average_rating": avg_rating,
            "sentiment_breakdown": {
                "Positive": pos_count,
                "Neutral": neu_count,
                "Negative": neg_count,
                "positive_pct": pos_pct,
                "neutral_pct": neu_pct,
                "negative_pct": neg_pct,
            },
            "rating_distribution": rating_dist,
            "top_complaints": top_complaints,
            "top_positives": top_positives,
            "ai_summary": summary_res.get("summary", ""),
        }

    def get_reviews_explorer(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str = "",
        product: str = "",
        sentiment: str = "",
        rating: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Explores customer reviews with text search, product filters, sentiment filters,
        rating filters, and page offset calculation.
        """
        if self.df is None or self.df.empty:
            return {"reviews": [], "total": 0, "page": page, "total_pages": 0}

        filtered = self.df

        if product and product.strip() and product.lower() != "all":
            filtered = filtered[filtered["Product_name"].str.lower() == product.strip().lower()]

        if sentiment and sentiment.strip() and sentiment.lower() != "all":
            filtered = filtered[filtered["sentiment"].str.lower() == sentiment.strip().lower()]

        if rating is not None and rating > 0:
            filtered = filtered[filtered["Rate"] == float(rating)]

        if search and search.strip():
            query_lower = search.lower().strip()
            filtered = filtered[
                filtered["full_review"].astype(str).str.lower().str.contains(query_lower, regex=False)
                | filtered["Product_name"].astype(str).str.lower().str.contains(query_lower, regex=False)
            ]

        total_records = int(len(filtered))
        total_pages = max(1, (total_records + page_size - 1) // page_size)
        current_page = max(1, min(page, total_pages))
        offset = (current_page - 1) * page_size

        page_df = filtered.iloc[offset : offset + page_size]

        reviews = [
            {
                "id": str(idx),
                "product": str(row.get("Product_name", "")),
                "rating": float(row.get("Rate", 0.0)),
                "sentiment": str(row.get("sentiment", "Neutral")),
                "text": str(row.get("full_review", row.get("Review", ""))),
            }
            for idx, row in page_df.iterrows()
        ]

        return {
            "reviews": reviews,
            "total": total_records,
            "page": current_page,
            "page_size": page_size,
            "total_pages": total_pages,
        }


@lru_cache()
def get_analytics_service() -> AnalyticsService:
    """
    Singleton accessor function for AnalyticsService.
    """
    return AnalyticsService()
