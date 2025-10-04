"""
Main Image Similarity Calculator

Orchestrates the calculation of similarity between two product images
using multiple feature extractors and weighted scoring.
"""

import os
import cv2
import numpy as np
from typing import Tuple, Dict, List
from .feature_extractors import SIFTExtractor, ColorExtractor, SSIMExtractor, EdgeExtractor, ShapeExtractor
from .config import SimilarityConfig, DEFAULT_CONFIG


class ImageSimilarityCalculator:
    """Main class for calculating image similarity."""
    
    def __init__(self, config: SimilarityConfig = None):
        """
        Initialize the similarity calculator.
        
        Args:
            config: Configuration object. Uses default if None.
        """
        self.config = config or DEFAULT_CONFIG
        
        # Initialize feature extractors
        self.sift_extractor = SIFTExtractor(self.config)
        self.color_extractor = ColorExtractor(self.config)
        self.ssim_extractor = SSIMExtractor(self.config)
        self.edge_extractor = EdgeExtractor(self.config)
        self.shape_extractor = ShapeExtractor(self.config)
    
    def calculate_similarity(self, image_path1: str, image_path2: str) -> float:
        """
        Calculate semantic similarity between two product images.
        
        Args:
            image_path1: Path to first image file
            image_path2: Path to second image file
            
        Returns:
            Similarity score between 0.0 and 1.0 (1.0 = identical)
        """
        try:
            # Load and preprocess images
            img1, img2 = self._load_and_preprocess_images(image_path1, image_path2)
            
            if img1 is None or img2 is None:
                print(f"❌ Error loading images: {image_path1} or {image_path2}")
                return 0.0
            
            # Calculate different similarity metrics
            similarities = self._calculate_all_similarities(img1, img2)
            
            # Calculate weighted average
            total_score = sum(score * weight for _, score, weight in similarities)
            
            # Debug output
            self._print_similarity_analysis(similarities, total_score)
            
            return min(1.0, max(0.0, total_score))
            
        except Exception as e:
            return 0.0
    
    def _load_and_preprocess_images(self, path1: str, path2: str) -> Tuple[np.ndarray, np.ndarray]:
        """Load and preprocess images for comparison."""
        try:
            # Check if files exist
            if not os.path.exists(path1):
                print(f"❌ Image file not found: {path1}")
                return None, None
            if not os.path.exists(path2):
                print(f"❌ Image file not found: {path2}")
                return None, None
            
            # Load images
            img1 = cv2.imread(path1)
            img2 = cv2.imread(path2)
            
            if img1 is None or img2 is None:
                return None, None
            
            # Images loaded successfully
            
            # Resize images to same size for comparison
            img1_resized = cv2.resize(img1, self.config.RESIZE_DIMENSIONS)
            img2_resized = cv2.resize(img2, self.config.RESIZE_DIMENSIONS)
            
            return img1_resized, img2_resized
            
        except Exception as e:
            return None, None
    
    def _calculate_all_similarities(self, img1: np.ndarray, img2: np.ndarray) -> List[Tuple[str, float, float]]:
        """Calculate all similarity metrics."""
        # Convert to grayscale for some operations
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        similarities = []
        
        # 1. Color Histogram Comparison
        color_features1 = self.color_extractor.extract_features(img1)
        color_features2 = self.color_extractor.extract_features(img2)
        color_score = self.color_extractor.calculate_similarity(color_features1, color_features2)
        similarities.append(('Color', color_score, self.config.COLOR_WEIGHT))
        
        # 2. SIFT Feature Matching
        sift_features1 = self.sift_extractor.extract_features(gray1)
        sift_features2 = self.sift_extractor.extract_features(gray2)
        sift_score = self.sift_extractor.calculate_similarity(sift_features1, sift_features2)
        similarities.append(('SIFT', sift_score, self.config.SIFT_WEIGHT))
        
        # 3. Structural Similarity
        ssim_features1 = self.ssim_extractor.extract_features(gray1)
        ssim_features2 = self.ssim_extractor.extract_features(gray2)
        ssim_score = self.ssim_extractor.calculate_similarity(ssim_features1, ssim_features2)
        similarities.append(('SSIM', ssim_score, self.config.SSIM_WEIGHT))
        
        # 4. Edge Detection Similarity
        edge_features1 = self.edge_extractor.extract_features(gray1)
        edge_features2 = self.edge_extractor.extract_features(gray2)
        edge_score = self.edge_extractor.calculate_similarity(edge_features1, edge_features2)
        similarities.append(('Edge', edge_score, self.config.EDGE_WEIGHT))
        
        # 5. Shape Analysis
        shape_features1 = self.shape_extractor.extract_features(gray1)
        shape_features2 = self.shape_extractor.extract_features(gray2)
        shape_score = self.shape_extractor.calculate_similarity(shape_features1, shape_features2)
        similarities.append(('Shape', shape_score, self.config.SHAPE_WEIGHT))
        
        return similarities
    
    def _print_similarity_analysis(self, similarities: List[Tuple[str, float, float]], total_score: float):
        """Print detailed similarity analysis (optional debug output)."""
        # Uncomment for debug output:
        # print(f"🔍 Image Similarity Analysis:")
        # for name, score, weight in similarities:
        #     print(f"   {name}: {score:.3f} (weight: {weight})")
        # print(f"   Final Score: {total_score:.3f}")
        pass
    
    def get_detailed_analysis(self, image_path1: str, image_path2: str) -> Dict:
        """
        Get detailed analysis of image similarity.
        
        Args:
            image_path1: Path to first image file
            image_path2: Path to second image file
            
        Returns:
            Dictionary with detailed analysis results
        """
        try:
            # Load images for metadata
            img1 = cv2.imread(image_path1)
            img2 = cv2.imread(image_path2)
            
            if img1 is None or img2 is None:
                return {"error": f"Could not load images: {image_path1} or {image_path2}"}
            
            # Calculate similarity
            similarity_score = self.calculate_similarity(image_path1, image_path2)
            
            # Get individual metrics
            img1_resized, img2_resized = self._load_and_preprocess_images(image_path1, image_path2)
            gray1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2GRAY)
            
            similarities = self._calculate_all_similarities(img1_resized, img2_resized)
            
            return {
                "similarity_score": round(similarity_score, 3),
                "individual_scores": {name: round(score, 3) for name, score, _ in similarities},
                "weights": {name: weight for name, _, weight in similarities},
                "image1_metadata": {
                    "dimensions": f"{img1.shape[1]}x{img1.shape[0]}",
                    "channels": img1.shape[2] if len(img1.shape) > 2 else 1
                },
                "image2_metadata": {
                    "dimensions": f"{img2.shape[1]}x{img2.shape[0]}",
                    "channels": img2.shape[2] if len(img2.shape) > 2 else 1
                }
            }
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
