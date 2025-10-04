"""
Configuration for Image Similarity Calculations

Contains default parameters, weights, and thresholds for various
similarity calculation methods.
"""

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class SimilarityConfig:
    """Configuration class for image similarity calculations."""
    
    # Image preprocessing
    RESIZE_DIMENSIONS: Tuple[int, int] = (400, 400)
    
    # Feature extraction parameters (strict for product differentiation)
    SIFT_N_FEATURES: int = 1000
    SIFT_LOWE_RATIO_FLANN: float = 0.65  # Very strict FLANN matching
    SIFT_LOWE_RATIO_BF: float = 0.6      # Very strict brute force matching
    
    # Edge detection parameters (more adaptive)
    CANNY_LOWER_FACTOR: float = 0.6      # More sensitive edge detection
    CANNY_UPPER_FACTOR: float = 1.4      # More inclusive edge detection
    
    # Similarity weights (strict for product differentiation)
    COLOR_WEIGHT: float = 0.50           # Major emphasis - color is key differentiator
    SIFT_WEIGHT: float = 0.15            # Reduced - too generic for different products
    SSIM_WEIGHT: float = 0.25            # Increased - structural differences matter most
    EDGE_WEIGHT: float = 0.10            # Reduced - less important for product differentiation
    SHAPE_WEIGHT: float = 0.00           # Disabled - shape varies too much with perspective
    
    # Matching thresholds (loosened for better detection)
    DEFAULT_MATCH_THRESHOLD: float = 0.6  # Lowered from 0.7
    HIGH_CONFIDENCE_THRESHOLD: float = 0.75  # Lowered from 0.8
    MEDIUM_CONFIDENCE_THRESHOLD: float = 0.45  # Lowered from 0.5
    
    # Analysis parameters
    MAX_POSSIBLE_DISTANCE_FACTOR: float = 255.0
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        total_weight = (self.COLOR_WEIGHT + self.SIFT_WEIGHT + 
                       self.SSIM_WEIGHT + self.EDGE_WEIGHT + self.SHAPE_WEIGHT)
        
        if not abs(total_weight - 1.0) < 0.001:
            raise ValueError(f"Similarity weights must sum to 1.0, got {total_weight}")
        
        if not (0.0 <= self.DEFAULT_MATCH_THRESHOLD <= 1.0):
            raise ValueError(f"Match threshold must be between 0.0 and 1.0, got {self.DEFAULT_MATCH_THRESHOLD}")


# Default configuration instance
DEFAULT_CONFIG = SimilarityConfig()


# Similarity interpretation thresholds (loosened for better product matching)
SIMILARITY_INTERPRETATIONS = {
    "Very High": (0.75, 1.0),    # Lowered from 0.8
    "High": (0.6, 0.75),         # Adjusted range
    "Medium": (0.4, 0.6),        # Kept same
    "Low": (0.25, 0.4),          # Lowered from 0.2
    "Very Low": (0.0, 0.25)      # Adjusted range
}


def get_similarity_interpretation(score: float) -> str:
    """Get human-readable interpretation of similarity score."""
    for interpretation, (min_score, max_score) in SIMILARITY_INTERPRETATIONS.items():
        if min_score <= score < max_score:
            return interpretation
    return "Very Low"  # Fallback for edge cases


def get_confidence_level(score: float) -> str:
    """Get confidence level based on similarity score."""
    if score >= DEFAULT_CONFIG.HIGH_CONFIDENCE_THRESHOLD:
        return "High"
    elif score >= DEFAULT_CONFIG.MEDIUM_CONFIDENCE_THRESHOLD:
        return "Medium"
    else:
        return "Low"
