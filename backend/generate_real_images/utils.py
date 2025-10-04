"""
Utility Functions

Helper functions for similarity scoring, URL processing, image similarity, etc.
"""

import os
import cv2
import numpy as np
from typing import Dict, Tuple, Optional
from PIL import Image
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


def calculate_image_similarity(image_path1: str, image_path2: str) -> float:
    """
    Calculate semantic similarity between two product images.
    
    Uses the organized image similarity system with multiple computer vision techniques.
    
    Args:
        image_path1: Path to first image file
        image_path2: Path to second image file
        
    Returns:
        Similarity score between 0.0 and 1.0 (1.0 = identical)
    """
    try:
        from image_similarity_scores import ImageSimilarityCalculator
        
        calculator = ImageSimilarityCalculator()
        return calculator.calculate_similarity(image_path1, image_path2)
        
    except ImportError:
        return _calculate_image_similarity_fallback(image_path1, image_path2)
    except Exception as e:
        return 0.0


def _calculate_image_similarity_fallback(image_path1: str, image_path2: str) -> float:
    """Fallback similarity calculation if organized module is not available."""
    try:
        # Load images
        img1 = cv2.imread(image_path1)
        img2 = cv2.imread(image_path2)
        
        if img1 is None or img2 is None:
            print(f"❌ Error loading images: {image_path1} or {image_path2}")
            return 0.0
        
        # Resize images to same size for comparison
        img1_resized = cv2.resize(img1, (400, 400))
        img2_resized = cv2.resize(img2, (400, 400))
        
        # Convert to grayscale for some operations
        gray1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2GRAY)
        
        # Calculate different similarity metrics
        similarities = []
        
        # 1. Color Histogram Comparison (35% weight) - Most reliable for similar products
        color_score = _calculate_color_similarity(img1_resized, img2_resized)
        similarities.append(('Color', color_score, 0.35))
        
        # 2. SIFT Feature Matching (25% weight)
        sift_score = _calculate_sift_similarity(gray1, gray2)
        similarities.append(('SIFT', sift_score, 0.25))
        
        # 3. Structural Similarity (20% weight)
        ssim_score = _calculate_ssim_similarity(gray1, gray2)
        similarities.append(('SSIM', ssim_score, 0.2))
        
        # 4. Edge Detection Similarity (15% weight)
        edge_score = _calculate_edge_similarity(gray1, gray2)
        similarities.append(('Edge', edge_score, 0.15))
        
        # 5. Shape Analysis (5% weight)
        shape_score = _calculate_shape_similarity(gray1, gray2)
        similarities.append(('Shape', shape_score, 0.05))
        
        # Calculate weighted average
        total_score = sum(score * weight for _, score, weight in similarities)
        
        return min(1.0, max(0.0, total_score))
        
    except Exception as e:
        return 0.0


def _calculate_sift_similarity(gray1: np.ndarray, gray2: np.ndarray) -> float:
    """Calculate SIFT feature matching similarity."""
    try:
        # Initialize SIFT detector with more keypoints
        sift = cv2.SIFT_create(nfeatures=1000)
        
        # Find keypoints and descriptors
        kp1, des1 = sift.detectAndCompute(gray1, None)
        kp2, des2 = sift.detectAndCompute(gray2, None)
        
        if des1 is None or des2 is None or len(des1) < 2 or len(des2) < 2:
            return 0.0
        
        # Try multiple matching strategies
        similarities = []
        
        # Strategy 1: FLANN matcher
        try:
            FLANN_INDEX_KDTREE = 1
            index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
            search_params = dict(checks=50)
            flann = cv2.FlannBasedMatcher(index_params, search_params)
            
            matches = flann.knnMatch(des1, des2, k=2)
            
            # Apply Lowe's ratio test with more lenient threshold
            good_matches = []
            for match_pair in matches:
                if len(match_pair) == 2:
                    m, n = match_pair
                    if m.distance < 0.8 * n.distance:  # More lenient threshold
                        good_matches.append(m)
            
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
            
            good_matches = []
            for match_pair in matches:
                if len(match_pair) == 2:
                    m, n = match_pair
                    if m.distance < 0.75 * n.distance:
                        good_matches.append(m)
            
            if len(good_matches) > 0:
                min_keypoints = min(len(kp1), len(kp2))
                similarity = len(good_matches) / min_keypoints
                similarities.append(min(1.0, similarity))
        except:
            pass
        
        # Strategy 3: Simple distance-based matching
        try:
            if len(des1) > 0 and len(des2) > 0:
                # Calculate pairwise distances
                distances = []
                for d1 in des1:
                    min_dist = float('inf')
                    for d2 in des2:
                        dist = np.linalg.norm(d1 - d2)
                        min_dist = min(min_dist, dist)
                    distances.append(min_dist)
                
                # Convert distances to similarity (lower distance = higher similarity)
                avg_distance = np.mean(distances)
                max_possible_distance = np.sqrt(len(des1[0]) * 255**2)  # Maximum possible distance
                similarity = 1.0 - (avg_distance / max_possible_distance)
                similarities.append(max(0.0, similarity))
        except:
            pass
        
        # Return the best similarity score
        if similarities:
            return max(similarities)
        else:
            return 0.0
        
    except Exception as e:
        print(f"⚠️  SIFT calculation error: {e}")
        return 0.0


def _calculate_color_similarity(img1: np.ndarray, img2: np.ndarray) -> float:
    """Calculate color histogram similarity."""
    try:
        # Calculate histograms for each channel
        hist1 = []
        hist2 = []
        
        for i in range(3):  # BGR channels
            hist1.append(cv2.calcHist([img1], [i], None, [256], [0, 256]))
            hist2.append(cv2.calcHist([img2], [i], None, [256], [0, 256]))
        
        # Calculate correlation for each channel
        correlations = []
        for h1, h2 in zip(hist1, hist2):
            corr = cv2.compareHist(h1, h2, cv2.HISTCMP_CORREL)
            correlations.append(corr)
        
        # Return average correlation
        return max(0.0, np.mean(correlations))
        
    except Exception as e:
        print(f"⚠️  Color calculation error: {e}")
        return 0.0


def _calculate_ssim_similarity(gray1: np.ndarray, gray2: np.ndarray) -> float:
    """Calculate Structural Similarity Index (SSIM)."""
    try:
        # Ensure images are the same size
        if gray1.shape != gray2.shape:
            gray2 = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))
        
        # Use OpenCV's built-in template matching as fallback
        # This is more reliable than scikit-image for this use case
        try:
            # Normalize images
            gray1_norm = cv2.normalize(gray1, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            gray2_norm = cv2.normalize(gray2, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            
            # Use template matching
            result = cv2.matchTemplate(gray1_norm, gray2_norm, cv2.TM_CCOEFF_NORMED)
            correlation = result[0][0]
            
            # Convert to similarity score
            return max(0.0, correlation)
            
        except Exception as e:
            print(f"⚠️  Template matching error: {e}")
            return 0.0
            
    except Exception as e:
        print(f"⚠️  SSIM calculation error: {e}")
        return 0.0


def _calculate_edge_similarity(gray1: np.ndarray, gray2: np.ndarray) -> float:
    """Calculate edge detection similarity."""
    try:
        # Apply Canny edge detection with adaptive thresholds
        # Calculate thresholds based on image statistics
        median1 = np.median(gray1)
        median2 = np.median(gray2)
        
        lower1 = int(max(0, 0.7 * median1))
        upper1 = int(min(255, 1.3 * median1))
        lower2 = int(max(0, 0.7 * median2))
        upper2 = int(min(255, 1.3 * median2))
        
        edges1 = cv2.Canny(gray1, lower1, upper1)
        edges2 = cv2.Canny(gray2, lower2, upper2)
        
        # Try multiple comparison methods
        similarities = []
        
        # Method 1: Template matching
        try:
            correlation = cv2.matchTemplate(edges1, edges2, cv2.TM_CCOEFF_NORMED)[0][0]
            similarities.append(max(0.0, correlation))
        except:
            pass
        
        # Method 2: Histogram comparison
        try:
            hist1 = cv2.calcHist([edges1], [0], None, [256], [0, 256])
            hist2 = cv2.calcHist([edges2], [0], None, [256], [0, 256])
            correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            similarities.append(max(0.0, correlation))
        except:
            pass
        
        # Method 3: Structural similarity of edges
        try:
            # Calculate edge density
            edge_density1 = np.sum(edges1 > 0) / edges1.size
            edge_density2 = np.sum(edges2 > 0) / edges2.size
            
            # Calculate similarity based on edge density
            density_similarity = 1.0 - abs(edge_density1 - edge_density2)
            similarities.append(max(0.0, density_similarity))
        except:
            pass
        
        # Return the best similarity score
        if similarities:
            return max(similarities)
        else:
            return 0.0
        
    except Exception as e:
        print(f"⚠️  Edge calculation error: {e}")
        return 0.0


def _calculate_shape_similarity(gray1: np.ndarray, gray2: np.ndarray) -> float:
    """Calculate shape similarity using contour analysis."""
    try:
        # Find contours
        contours1, _ = cv2.findContours(gray1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours2, _ = cv2.findContours(gray2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours1 or not contours2:
            return 0.0
        
        # Get largest contour from each image
        largest_contour1 = max(contours1, key=cv2.contourArea)
        largest_contour2 = max(contours2, key=cv2.contourArea)
        
        # Calculate Hu moments
        moments1 = cv2.moments(largest_contour1)
        moments2 = cv2.moments(largest_contour2)
        
        if moments1['m00'] == 0 or moments2['m00'] == 0:
            return 0.0
        
        # Calculate Hu moments
        hu1 = cv2.HuMoments(moments1).flatten()
        hu2 = cv2.HuMoments(moments2).flatten()
        
        # Calculate similarity using Hu moments
        # Apply log transform to reduce scale differences
        hu1 = -np.sign(hu1) * np.log10(np.abs(hu1) + 1e-10)
        hu2 = -np.sign(hu2) * np.log10(np.abs(hu2) + 1e-10)
        
        # Calculate Euclidean distance
        distance = np.linalg.norm(hu1 - hu2)
        
        # Convert distance to similarity (inverse relationship)
        similarity = 1.0 / (1.0 + distance)
        
        return min(1.0, similarity)
        
    except Exception as e:
        print(f"⚠️  Shape calculation error: {e}")
        return 0.0


def compare_product_images(image_path1: str, image_path2: str, threshold: float = 0.7) -> Dict:
    """
    Compare two product images and provide detailed analysis.
    
    Uses the organized image similarity system for comprehensive analysis.
    
    Args:
        image_path1: Path to first image file
        image_path2: Path to second image file
        threshold: Similarity threshold for match determination
        
    Returns:
        Dictionary with similarity analysis results
    """
    try:
        from image_similarity_scores import ComparisonAnalyzer
        
        analyzer = ComparisonAnalyzer()
        return analyzer.compare_images(image_path1, image_path2, threshold)
        
    except ImportError:
        return _compare_product_images_fallback(image_path1, image_path2, threshold)
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}


def _compare_product_images_fallback(image_path1: str, image_path2: str, threshold: float = 0.7) -> Dict:
    """Fallback comparison if organized module is not available."""
    try:
        # Check if files exist
        if not os.path.exists(image_path1):
            return {"error": f"Image file not found: {image_path1}"}
        if not os.path.exists(image_path2):
            return {"error": f"Image file not found: {image_path2}"}
        
        # Calculate similarity
        similarity_score = calculate_image_similarity(image_path1, image_path2)
        
        # Determine match status
        is_match = similarity_score >= threshold
        match_status = "MATCH" if is_match else "NO MATCH"
        
        # Load images for additional analysis
        img1 = cv2.imread(image_path1)
        img2 = cv2.imread(image_path2)
        
        # Get image dimensions
        height1, width1 = img1.shape[:2] if img1 is not None else (0, 0)
        height2, width2 = img2.shape[:2] if img2 is not None else (0, 0)
        
        return {
            "similarity_score": round(similarity_score, 3),
            "is_match": is_match,
            "match_status": match_status,
            "threshold": threshold,
            "image1": {
                "path": image_path1,
                "dimensions": f"{width1}x{height1}",
                "size_kb": round(os.path.getsize(image_path1) / 1024, 1)
            },
            "image2": {
                "path": image_path2,
                "dimensions": f"{width2}x{height2}",
                "size_kb": round(os.path.getsize(image_path2) / 1024, 1)
            },
            "analysis": {
                "confidence": "High" if similarity_score > 0.8 else "Medium" if similarity_score > 0.5 else "Low",
                "recommendation": "Likely same product" if is_match else "Different products or poor match"
            }
        }
        
    except Exception as e:
        return {"error": f"Fallback analysis failed: {str(e)}"}

