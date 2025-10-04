"""
Feature Extractors for Image Similarity

Contains individual feature extraction classes for different similarity metrics:
- SIFT feature matching
- Color histogram analysis
- Structural similarity (SSIM)
- Edge detection
- Shape analysis
"""

import cv2
import numpy as np
from abc import ABC, abstractmethod
from typing import Tuple, List, Optional
from .config import SimilarityConfig


class BaseFeatureExtractor(ABC):
    """Base class for feature extractors."""
    
    def __init__(self, config: SimilarityConfig):
        self.config = config
    
    @abstractmethod
    def extract_features(self, image: np.ndarray) -> np.ndarray:
        """Extract features from image."""
        pass
    
    @abstractmethod
    def calculate_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """Calculate similarity between two feature sets."""
        pass


class SIFTExtractor(BaseFeatureExtractor):
    """SIFT feature extraction and matching."""
    
    def __init__(self, config: SimilarityConfig):
        super().__init__(config)
        self.sift = cv2.SIFT_create(nfeatures=config.SIFT_N_FEATURES)
    
    def extract_features(self, image: np.ndarray) -> Tuple[List, Optional[np.ndarray]]:
        """Extract SIFT keypoints and descriptors with lighting normalization."""
        # Apply histogram equalization for better lighting robustness
        if len(image.shape) == 3:
            # Convert to LAB color space for better lighting normalization
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            lab[:,:,0] = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(lab[:,:,0])
            normalized_image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            normalized_image = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(image)
        
        # Convert to grayscale for SIFT
        if len(normalized_image.shape) == 3:
            gray = cv2.cvtColor(normalized_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = normalized_image
        
        keypoints, descriptors = self.sift.detectAndCompute(gray, None)
        return keypoints, descriptors
    
    def calculate_similarity(self, features1: Tuple, features2: Tuple) -> float:
        """Calculate SIFT similarity using multiple matching strategies."""
        try:
            kp1, des1 = features1
            kp2, des2 = features2
            
            if des1 is None or des2 is None or len(des1) < 2 or len(des2) < 2:
                return 0.0
            
            similarities = []
            
            # Strategy 1: FLANN matcher
            try:
                FLANN_INDEX_KDTREE = 1
                index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
                search_params = dict(checks=50)
                flann = cv2.FlannBasedMatcher(index_params, search_params)
                
                matches = flann.knnMatch(des1, des2, k=2)
                good_matches = self._apply_lowe_ratio_test(matches, self.config.SIFT_LOWE_RATIO_FLANN)
                
                if len(good_matches) > 0:
                    min_keypoints = min(len(kp1), len(kp2))
                    similarity = len(good_matches) / min_keypoints
                    similarities.append(min(1.0, similarity))
            except:
                pass
            
            # Strategy 2: Brute Force matcher
            try:
                bf = cv2.BFMatcher()
                matches = bf.knnMatch(des1, des2, k=2)
                good_matches = self._apply_lowe_ratio_test(matches, self.config.SIFT_LOWE_RATIO_BF)
                
                if len(good_matches) > 0:
                    min_keypoints = min(len(kp1), len(kp2))
                    similarity = len(good_matches) / min_keypoints
                    similarities.append(min(1.0, similarity))
            except:
                pass
            
            # Strategy 3: Distance-based matching
            try:
                if len(des1) > 0 and len(des2) > 0:
                    distances = []
                    for d1 in des1:
                        min_dist = float('inf')
                        for d2 in des2:
                            dist = np.linalg.norm(d1 - d2)
                            min_dist = min(min_dist, dist)
                        distances.append(min_dist)
                    
                    avg_distance = np.mean(distances)
                    max_possible_distance = np.sqrt(len(des1[0]) * self.config.MAX_POSSIBLE_DISTANCE_FACTOR**2)
                    # Strict distance scoring - no boost for conservative scoring
                    similarity = 1.0 - (avg_distance / max_possible_distance)
                    similarities.append(max(0.0, similarity))
            except:
                pass
            
            return max(similarities) if similarities else 0.0
            
        except Exception as e:
            return 0.0
    
    def _apply_lowe_ratio_test(self, matches: List, ratio: float) -> List:
        """Apply Lowe's ratio test to filter good matches."""
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < ratio * n.distance:
                    good_matches.append(m)
        return good_matches


class ColorExtractor(BaseFeatureExtractor):
    """Color histogram analysis."""
    
    def extract_features(self, image: np.ndarray) -> List[np.ndarray]:
        """Extract color histograms for each channel with lighting normalization."""
        histograms = []
        
        # Normalize image for lighting variations
        normalized_image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
        
        # Convert to different color spaces for better lighting robustness
        hsv_image = cv2.cvtColor(normalized_image, cv2.COLOR_BGR2HSV)
        lab_image = cv2.cvtColor(normalized_image, cv2.COLOR_BGR2LAB)
        
        # Extract histograms from multiple color spaces
        for i in range(3):  # BGR channels
            hist = cv2.calcHist([normalized_image], [i], None, [64], [0, 256])  # Reduced bins for robustness
            histograms.append(hist)
        
        # Add HSV histograms (more lighting-invariant)
        for i in range(3):  # HSV channels
            hist = cv2.calcHist([hsv_image], [i], None, [32], [0, 256])
            histograms.append(hist)
        
        return histograms
    
    def calculate_similarity(self, features1: List[np.ndarray], features2: List[np.ndarray]) -> float:
        """Calculate color histogram similarity with lighting robustness."""
        try:
            correlations = []
            
            # Process BGR histograms (first 3)
            bgr_correlations = []
            for i in range(3):
                corr = cv2.compareHist(features1[i], features2[i], cv2.HISTCMP_CORREL)
                # No boost - use raw correlation for strict scoring
                bgr_correlations.append(corr)
            
            # Process HSV histograms (more lighting-invariant, last 3)
            hsv_correlations = []
            for i in range(3, 6):
                if i < len(features1) and i < len(features2):
                    corr = cv2.compareHist(features1[i], features2[i], cv2.HISTCMP_CORREL)
                    # No boost - use raw correlation for strict scoring
                    hsv_correlations.append(corr)
            
            # Use minimum of both scores for strict product differentiation
            if hsv_correlations and bgr_correlations:
                hsv_score = max(hsv_correlations)
                bgr_score = max(bgr_correlations)
                # Use minimum for strict differentiation - both must be similar
                final_score = min(hsv_score, bgr_score)
            elif hsv_correlations:
                final_score = max(hsv_correlations)
            elif bgr_correlations:
                final_score = max(bgr_correlations)
            else:
                final_score = 0.0
            
            return max(0.0, final_score)
            
        except Exception as e:
            return 0.0


class SSIMExtractor(BaseFeatureExtractor):
    """Structural Similarity Index calculation."""
    
    def extract_features(self, image: np.ndarray) -> np.ndarray:
        """Normalize image for SSIM calculation."""
        return cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    
    def calculate_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """Calculate structural similarity using template matching."""
        try:
            # Ensure images are the same size
            if features1.shape != features2.shape:
                features2 = cv2.resize(features2, (features1.shape[1], features1.shape[0]))
            
            # Use template matching as SSIM approximation
            result = cv2.matchTemplate(features1, features2, cv2.TM_CCOEFF_NORMED)
            correlation = result[0][0]
            
            return max(0.0, correlation)
            
        except Exception as e:
            return 0.0


class EdgeExtractor(BaseFeatureExtractor):
    """Edge detection and analysis."""
    
    def extract_features(self, image: np.ndarray) -> np.ndarray:
        """Extract edge features using adaptive Canny edge detection with lighting normalization."""
        # Normalize image for lighting variations
        if len(image.shape) == 3:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply histogram equalization for better lighting robustness
        normalized_gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(gray)
        
        # Calculate adaptive thresholds on normalized image
        median = np.median(normalized_gray)
        lower = int(max(0, self.config.CANNY_LOWER_FACTOR * median))
        upper = int(min(255, self.config.CANNY_UPPER_FACTOR * median))
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(normalized_gray, (3, 3), 0)
        
        edges = cv2.Canny(blurred, lower, upper)
        return edges
    
    def calculate_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """Calculate edge similarity using multiple methods."""
        try:
            similarities = []
            
            # Method 1: Template matching
            try:
                correlation = cv2.matchTemplate(features1, features2, cv2.TM_CCOEFF_NORMED)[0][0]
                similarities.append(max(0.0, correlation))
            except:
                pass
            
            # Method 2: Histogram comparison
            try:
                hist1 = cv2.calcHist([features1], [0], None, [256], [0, 256])
                hist2 = cv2.calcHist([features2], [0], None, [256], [0, 256])
                correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
                similarities.append(max(0.0, correlation))
            except:
                pass
            
            # Method 3: Edge density similarity
            try:
                edge_density1 = np.sum(features1 > 0) / features1.size
                edge_density2 = np.sum(features2 > 0) / features2.size
                density_similarity = 1.0 - abs(edge_density1 - edge_density2)
                similarities.append(max(0.0, density_similarity))
            except:
                pass
            
            return max(similarities) if similarities else 0.0
            
        except Exception as e:
            return 0.0


class ShapeExtractor(BaseFeatureExtractor):
    """Shape analysis using contour and moment analysis."""
    
    def extract_features(self, image: np.ndarray) -> np.ndarray:
        """Extract shape features using Hu moments."""
        try:
            # Find contours
            contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return np.array([])
            
            # Get largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Calculate Hu moments
            moments = cv2.moments(largest_contour)
            if moments['m00'] == 0:
                return np.array([])
            
            hu_moments = cv2.HuMoments(moments).flatten()
            
            # Apply log transform to reduce scale differences
            hu_moments = -np.sign(hu_moments) * np.log10(np.abs(hu_moments) + 1e-10)
            
            return hu_moments
            
        except Exception as e:
            return np.array([])
    
    def calculate_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """Calculate shape similarity using Hu moments."""
        try:
            if len(features1) == 0 or len(features2) == 0:
                return 0.0
            
            # Calculate Euclidean distance
            distance = np.linalg.norm(features1 - features2)
            
            # Convert distance to similarity (inverse relationship)
            similarity = 1.0 / (1.0 + distance)
            
            return min(1.0, similarity)
            
        except Exception as e:
            return 0.0
