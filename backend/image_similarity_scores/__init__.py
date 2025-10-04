"""
Image Similarity Scores Package

A comprehensive system for calculating semantic similarity between product images
using multiple computer vision techniques including SIFT, color analysis, SSIM,
edge detection, and shape analysis.
"""

from .similarity_calculator import ImageSimilarityCalculator
from .feature_extractors import SIFTExtractor, ColorExtractor, SSIMExtractor, EdgeExtractor, ShapeExtractor
from .comparison_analyzer import ComparisonAnalyzer
from .config import SimilarityConfig

__version__ = "1.0.0"
__all__ = [
    'ImageSimilarityCalculator',
    'SIFTExtractor',
    'ColorExtractor', 
    'SSIMExtractor',
    'EdgeExtractor',
    'ShapeExtractor',
    'ComparisonAnalyzer',
    'SimilarityConfig'
]
