"""
Utility Functions

Helper functions for similarity scoring, URL processing, etc.
"""

from typing import Dict
from .config import EXACT_MATCH_KEYWORDS, GENERIC_KEYWORDS


def calculate_similarity_score(result: Dict, original_url: str) -> float:
    """
    Calculate similarity score based on title, snippet, and image quality.
    
    Args:
        result: Search result dictionary
        original_url: Original image URL for comparison
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    try:
        text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
        score = 0.5  # Base score
        
        # Positive indicators
        score += 0.1 * sum(1 for kw in EXACT_MATCH_KEYWORDS if kw in text)
        
        # Negative indicators
        score -= 0.1 * sum(1 for kw in GENERIC_KEYWORDS if kw in text)
        
        # Brand consistency bonus
        brands = ['nike', 'adidas', 'louis vuitton']
        for brand in brands:
            if brand in original_url.lower() and brand in text:
                score += 0.2
                break
        
        # High resolution bonus
        if res := result.get('image_resolution', ''):
            try:
                if 'x' in res:
                    w, h = map(int, res.split('x'))
                    if w > 400 and h > 400:
                        score += 0.1
            except:
                pass
        
        return max(0.0, min(1.0, score))
    except:
        return 0.5


def extract_domain(url: str) -> str:
    """Extract clean domain from URL."""
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower()
        return domain.replace('www.', '')
    except:
        return ''


def is_valid_url(url: str) -> bool:
    """Check if URL is valid."""
    try:
        from urllib.parse import urlparse
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

