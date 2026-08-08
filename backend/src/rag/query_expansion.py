import logging
from typing import Dict, List, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)

# Default domain-specific query expansion dictionary for e-commerce reviews
DEFAULT_EXPANSION_MAP: Dict[str, List[str]] = {
    "battery": [
        "battery life",
        "battery backup",
        "battery drain",
        "battery performance",
        "charging",
        "charging speed",
        "power consumption",
    ],
    "camera": [
        "picture quality",
        "image quality",
        "photo",
        "video",
        "lens",
        "clarity",
        "night mode",
    ],
    "cooling": [
        "air flow",
        "cooling performance",
        "room cooling",
        "fan speed",
        "temperature",
        "heat dissipation",
    ],
    "quality": [
        "build quality",
        "material",
        "durability",
        "performance",
        "sturdiness",
    ],
    "display": [
        "screen",
        "brightness",
        "resolution",
        "touchscreen",
        "colors",
        "display quality",
    ],
    "sound": [
        "audio",
        "speaker",
        "volume",
        "bass",
        "sound quality",
        "noise",
    ],
    "delivery": [
        "shipping",
        "package",
        "late",
        "damage",
        "courier",
        "delivery time",
    ],
    "price": [
        "value for money",
        "costly",
        "expensive",
        "cheap",
        "worth",
        "pricing",
    ],
    "service": [
        "customer care",
        "warranty",
        "replacement",
        "repair",
        "support",
        "after sales",
    ],
    "heating": [
        "overheating",
        "warm",
        "thermal",
        "heat up",
        "hot",
    ],
    "noise": [
        "noisy",
        "sound level",
        "humming",
        "loud",
        "vibration",
    ],
}


class QueryExpander:
    """
    Query Expander for RAG semantic search.
    Enriches user search queries with domain-specific synonyms and related terms
    to increase vector recall when searching ChromaDB.
    """

    def __init__(self, expansion_map: Optional[Dict[str, List[str]]] = None):
        self.expansion_map = expansion_map if expansion_map is not None else DEFAULT_EXPANSION_MAP.copy()

    def expand(self, query: str) -> str:
        """
        Expands the user query string with relevant domain keywords.

        Args:
            query (str): Original user search question or prompt.

        Returns:
            str: Expanded query string containing original query + matched terms.
        """
        if not query or not query.strip():
            return ""

        query_lower = query.lower().strip()
        added_terms: List[str] = []

        for keyword, related_terms in self.expansion_map.items():
            if keyword in query_lower:
                for term in related_terms:
                    if term not in query_lower and term not in added_terms:
                        added_terms.append(term)

        if added_terms:
            expanded_query = f"{query_lower} {' '.join(added_terms)}"
            logger.debug(f"Expanded query '{query}' -> '{expanded_query}'")
            return expanded_query

        return query_lower

    def add_keyword(self, keyword: str, terms: List[str]) -> None:
        """
        Adds or updates expansion terms for a specific keyword.
        """
        kw = keyword.lower().strip()
        if kw in self.expansion_map:
            existing = set(self.expansion_map[kw])
            for t in terms:
                existing.add(t.lower().strip())
            self.expansion_map[kw] = list(existing)
        else:
            self.expansion_map[kw] = [t.lower().strip() for t in terms]

    def get_expansion_map(self) -> Dict[str, List[str]]:
        """
        Returns a copy of the current query expansion dictionary.
        """
        return self.expansion_map.copy()


@lru_cache()
def get_query_expander() -> QueryExpander:
    """
    Singleton accessor function for QueryExpander instance.
    """
    return QueryExpander()


def expand_query(query: str) -> str:
    """
    Helper function to quickly expand a query using the singleton QueryExpander.
    """
    expander = get_query_expander()
    return expander.expand(query)
