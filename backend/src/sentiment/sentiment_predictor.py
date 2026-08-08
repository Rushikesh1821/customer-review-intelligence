import logging
import warnings
from functools import lru_cache
from typing import Dict, List, Any, Tuple
import joblib
import numpy as np

from backend.config.settings import get_settings
from backend.src.utils.preprocessing import preprocess_text

logger = logging.getLogger(__name__)


class SentimentPredictor:
    """
    Singleton service class for Sentiment Analysis using pre-trained
    TF-IDF Vectorizer and Logistic Regression Model.
    """

    def __init__(self):
        self.settings = get_settings()
        self.model = None
        self.vectorizer = None
        self._is_loaded = False
        self._load_models()

    def _load_models(self) -> None:
        """
        Loads the TF-IDF vectorizer and Logistic Regression sentiment model from disk.
        """
        if self._is_loaded:
            return

        model_path = self.settings.SENTIMENT_MODEL_PATH
        vectorizer_path = self.settings.TFIDF_VECTORIZER_PATH

        if not model_path.exists():
            raise FileNotFoundError(f"Sentiment model file not found at: {model_path}")
        if not vectorizer_path.exists():
            raise FileNotFoundError(f"TF-IDF vectorizer file not found at: {vectorizer_path}")

        try:
            logger.info(f"Loading sentiment model from {model_path}")
            logger.info(f"Loading TF-IDF vectorizer from {vectorizer_path}")

            # Ignore sklearn version warnings during joblib unpickling
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                self.model = joblib.load(model_path)
                self.vectorizer = joblib.load(vectorizer_path)

            self._is_loaded = True
            logger.info("Sentiment model and vectorizer loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load sentiment prediction models: {e}")
            raise RuntimeError(f"Error loading sentiment models: {e}") from e

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predicts sentiment for a single review text string.

        Args:
            text (str): Input review string.

        Returns:
            Dict[str, Any]: Dictionary containing:
                - sentiment (str): Predicted class ('Positive', 'Neutral', 'Negative')
                - confidence (float): High confidence score (0.0 to 1.0)
                - probabilities (Dict[str, float]): Class probability breakdown
                - preprocessed_text (str): Cleaned and normalized text used for inference
        """
        if not text or not text.strip():
            return {
                "sentiment": "Neutral",
                "confidence": 0.5,
                "probabilities": {"Negative": 0.33, "Neutral": 0.34, "Positive": 0.33},
                "preprocessed_text": "",
            }

        processed_text = preprocess_text(text)
        if not processed_text:
            # If text contained no valid words after preprocessing
            return {
                "sentiment": "Neutral",
                "confidence": 0.5,
                "probabilities": {"Negative": 0.33, "Neutral": 0.34, "Positive": 0.33},
                "preprocessed_text": processed_text,
            }

        # Vectorize input text
        features = self.vectorizer.transform([processed_text])

        # Predict sentiment label and probabilities
        pred_label = self.model.predict(features)[0]
        probs = self.model.predict_proba(features)[0]

        # Map classes to probability scores
        prob_dict = {
            cls_name: float(np.round(prob, 4))
            for cls_name, prob in zip(self.model.classes_, probs)
        }

        # Highest class probability as confidence
        confidence = float(np.round(np.max(probs), 4))

        return {
            "sentiment": str(pred_label),
            "confidence": confidence,
            "probabilities": prob_dict,
            "preprocessed_text": processed_text,
        }

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Predicts sentiment for a list of review texts efficiently in batch.

        Args:
            texts (List[str]): List of review text strings.

        Returns:
            List[Dict[str, Any]]: List of prediction dictionaries.
        """
        if not texts:
            return []

        processed_texts = [preprocess_text(t) for t in texts]
        non_empty_indices = [i for i, t in enumerate(processed_texts) if t.strip()]

        # Default fallback for empty texts
        results = [
            {
                "sentiment": "Neutral",
                "confidence": 0.5,
                "probabilities": {"Negative": 0.33, "Neutral": 0.34, "Positive": 0.33},
                "preprocessed_text": processed_texts[i],
            }
            for i in range(len(texts))
        ]

        if not non_empty_indices:
            return results

        non_empty_texts = [processed_texts[i] for i in non_empty_indices]
        features = self.vectorizer.transform(non_empty_texts)

        preds = self.model.predict(features)
        probs_matrix = self.model.predict_proba(features)

        for idx, orig_idx in enumerate(non_empty_indices):
            pred_label = preds[idx]
            probs = probs_matrix[idx]

            prob_dict = {
                cls_name: float(np.round(prob, 4))
                for cls_name, prob in zip(self.model.classes_, probs)
            }
            confidence = float(np.round(np.max(probs), 4))

            results[orig_idx] = {
                "sentiment": str(pred_label),
                "confidence": confidence,
                "probabilities": prob_dict,
                "preprocessed_text": processed_texts[orig_idx],
            }

        return results


@lru_cache()
def get_sentiment_predictor() -> SentimentPredictor:
    """
    Singleton accessor function for SentimentPredictor.
    Loads models only once and reuses the instance across all API calls.
    """
    return SentimentPredictor()
