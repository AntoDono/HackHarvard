"""
Counterfeit Detection Package

A comprehensive system for detecting counterfeit products using Google Lens API,
dynamic trust scoring, and automatic brand identification.
"""

from .image_searcher import ReverseImageSearcher
from .brand_detector import BrandDetector
from .trust_scorer import TrustScorer
from .utils import calculate_image_similarity, compare_product_images
from .config import KNOWN_BRANDS, TRUST_SCORES

__version__ = "1.0.0"
__all__ = [
    'ReverseImageSearcher',
    'BrandDetector', 
    'TrustScorer',
    'calculate_image_similarity',
    'compare_product_images',
    'KNOWN_BRANDS',
    'TRUST_SCORES'
]

