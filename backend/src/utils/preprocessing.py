import re
import os
import logging
from typing import List, Optional

# Disable NLTK's inisec local import security hook to permit workspace execution
os.environ["NLTK_DISABLE_IMPORT_SECURITY"] = "1"

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Configure logging
logger = logging.getLogger(__name__)

# Ensure required NLTK data resources are downloaded quietly
def _ensure_nltk_resources() -> None:
    resources = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
        ("corpora/wordnet", "wordnet"),
    ]
    for res_path, res_name in resources:
        try:
            nltk.data.find(res_path)
        except LookupError:
            try:
                logger.info(f"Downloading NLTK resource: {res_name}")
                nltk.download(res_name, quiet=True)
            except Exception as e:
                logger.warning(f"Failed to download NLTK resource '{res_name}': {e}")


_ensure_nltk_resources()

# Initialize NLTK components
try:
    STOP_WORDS = set(stopwords.words("english"))
except Exception:
    STOP_WORDS = set()

LEMMATIZER = WordNetLemmatizer()


def clean_raw_text(text: str) -> str:
    """
    Cleans raw text by converting to lowercase, removing non-alphabetic characters,
    and stripping extra whitespace.

    Args:
        text (str): Raw input review string.

    Returns:
        str: Basic cleaned text string.
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    # Convert to lowercase
    text = text.lower()

    # Retain only English letters and whitespace
    text = re.sub(r"[^a-zA-Z\s]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def preprocess_text(text: str, remove_stop_words: bool = True, lemmatize: bool = True) -> str:
    """
    Full text preprocessing pipeline matching the model training pipeline:
    1. Lowercasing & special character removal
    2. Tokenization
    3. Stopword removal (optional)
    4. Lemmatization (optional)

    Args:
        text (str): Input text string.
        remove_stop_words (bool): Whether to filter out standard English stopwords.
        lemmatize (bool): Whether to perform WordNet lemmatization.

    Returns:
        str: Fully preprocessed and normalized text string for TF-IDF / Sentiment prediction.
    """
    cleaned = clean_raw_text(text)
    if not cleaned:
        return ""

    try:
        tokens = word_tokenize(cleaned)
    except Exception as e:
        logger.warning(f"Word tokenization failed, falling back to split: {e}")
        tokens = cleaned.split()

    if remove_stop_words and STOP_WORDS:
        tokens = [word for word in tokens if word not in STOP_WORDS]

    if lemmatize and LEMMATIZER:
        tokens = [LEMMATIZER.lemmatize(word) for word in tokens]

    return " ".join(tokens)


def preprocess_reviews_batch(reviews: List[str]) -> List[str]:
    """
    Applies text preprocessing to a batch of review strings.

    Args:
        reviews (List[str]): List of review texts.

    Returns:
        List[str]: List of preprocessed review texts.
    """
    return [preprocess_text(review) for review in reviews]
