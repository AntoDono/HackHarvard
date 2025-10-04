"""
Comparison Analyzer for Image Similarity

Provides high-level analysis and interpretation of image similarity results
for counterfeit detection and product authentication.
"""

import os
from typing import Dict, Optional
from .similarity_calculator import ImageSimilarityCalculator
from .config import SimilarityConfig, DEFAULT_CONFIG, get_similarity_interpretation, get_confidence_level


class ComparisonAnalyzer:
    """Analyzes image similarity results for counterfeit detection."""
    
    def __init__(self, config: SimilarityConfig = None):
        """
        Initialize the comparison analyzer.
        
        Args:
            config: Configuration object. Uses default if None.
        """
        self.config = config or DEFAULT_CONFIG
        self.similarity_calculator = ImageSimilarityCalculator(self.config)
    
    def compare_images(self, image_path1: str, image_path2: str, 
                      threshold: Optional[float] = None) -> Dict:
        """
        Compare two product images and provide detailed analysis.
        
        Args:
            image_path1: Path to first image file
            image_path2: Path to second image file
            threshold: Similarity threshold for match determination
            
        Returns:
            Dictionary with comprehensive analysis results
        """
        try:
            # Use default threshold if not provided
            if threshold is None:
                threshold = self.config.DEFAULT_MATCH_THRESHOLD
            
            # Check if files exist
            if not os.path.exists(image_path1):
                return {"error": f"Image file not found: {image_path1}"}
            if not os.path.exists(image_path2):
                return {"error": f"Image file not found: {image_path2}"}
            
            # Calculate similarity
            similarity_score = self.similarity_calculator.calculate_similarity(image_path1, image_path2)
            
            # Determine match status
            is_match = similarity_score >= threshold
            match_status = "MATCH" if is_match else "NO MATCH"
            
            # Get detailed analysis
            detailed_analysis = self.similarity_calculator.get_detailed_analysis(image_path1, image_path2)
            
            # Get image metadata
            image1_metadata = self._get_image_metadata(image_path1)
            image2_metadata = self._get_image_metadata(image_path2)
            
            # Generate analysis insights
            analysis_insights = self._generate_analysis_insights(similarity_score, is_match)
            
            return {
                "similarity_score": round(similarity_score, 3),
                "is_match": is_match,
                "match_status": match_status,
                "threshold": threshold,
                "image1": image1_metadata,
                "image2": image2_metadata,
                "analysis": analysis_insights,
                "detailed_scores": detailed_analysis.get("individual_scores", {}),
                "weights": detailed_analysis.get("weights", {}),
                "interpretation": get_similarity_interpretation(similarity_score),
                "confidence": get_confidence_level(similarity_score)
            }
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _get_image_metadata(self, image_path: str) -> Dict:
        """Get metadata for an image file."""
        try:
            import cv2
            
            # Get file size
            file_size_kb = round(os.path.getsize(image_path) / 1024, 1)
            
            # Load image to get dimensions
            img = cv2.imread(image_path)
            if img is not None:
                height, width = img.shape[:2]
                channels = img.shape[2] if len(img.shape) > 2 else 1
                dimensions = f"{width}x{height}"
            else:
                dimensions = "Unknown"
                channels = 0
            
            return {
                "path": image_path,
                "dimensions": dimensions,
                "channels": channels,
                "size_kb": file_size_kb
            }
            
        except Exception as e:
            return {
                "path": image_path,
                "dimensions": "Unknown",
                "channels": 0,
                "size_kb": 0,
                "error": str(e)
            }
    
    def _generate_analysis_insights(self, similarity_score: float, is_match: bool) -> Dict:
        """Generate analysis insights and recommendations."""
        confidence = get_confidence_level(similarity_score)
        interpretation = get_similarity_interpretation(similarity_score)
        
        # Generate recommendations based on similarity score
        if is_match and similarity_score >= self.config.HIGH_CONFIDENCE_THRESHOLD:
            recommendation = "Likely same product - High confidence match"
            counterfeit_risk = "Low"
            action = "Use as reference for authentication"
        elif is_match:
            recommendation = "Similar products - Moderate confidence match"
            counterfeit_risk = "Low to Medium"
            action = "Compare physical details carefully"
        elif similarity_score >= self.config.MEDIUM_CONFIDENCE_THRESHOLD:
            recommendation = "Some similarities found - Needs verification"
            counterfeit_risk = "Medium"
            action = "Check for differences in brand markings, colors, and quality"
        else:
            recommendation = "Different products or poor match"
            counterfeit_risk = "High"
            action = "Verify with official brand website and check for counterfeits"
        
        return {
            "confidence": confidence,
            "interpretation": interpretation,
            "recommendation": recommendation,
            "counterfeit_risk": counterfeit_risk,
            "suggested_action": action
        }
    
    def batch_compare(self, image_pairs: list, threshold: Optional[float] = None) -> Dict:
        """
        Compare multiple pairs of images in batch.
        
        Args:
            image_pairs: List of tuples (image_path1, image_path2)
            threshold: Similarity threshold for match determination
            
        Returns:
            Dictionary with results for all comparisons
        """
        results = {
            "total_comparisons": len(image_pairs),
            "matches": 0,
            "no_matches": 0,
            "errors": 0,
            "comparisons": []
        }
        
        for i, (path1, path2) in enumerate(image_pairs):
            try:
                comparison_result = self.compare_images(path1, path2, threshold)
                
                if "error" in comparison_result:
                    results["errors"] += 1
                    comparison_result["pair_index"] = i
                elif comparison_result["is_match"]:
                    results["matches"] += 1
                else:
                    results["no_matches"] += 1
                
                comparison_result["pair_index"] = i
                results["comparisons"].append(comparison_result)
                
            except Exception as e:
                results["errors"] += 1
                results["comparisons"].append({
                    "pair_index": i,
                    "error": f"Comparison failed: {str(e)}"
                })
        
        return results
    
    def get_counterfeit_detection_insights(self, comparison_result: Dict) -> Dict:
        """
        Get specific insights for counterfeit detection.
        
        Args:
            comparison_result: Result from compare_images method
            
        Returns:
            Dictionary with counterfeit detection insights
        """
        if "error" in comparison_result:
            return {"error": "Cannot analyze due to comparison error"}
        
        similarity_score = comparison_result["similarity_score"]
        is_match = comparison_result["is_match"]
        
        # Counterfeit detection logic (loosened for better product matching)
        if is_match and similarity_score >= 0.7:  # Lowered from 0.8
            verdict = "LIKELY AUTHENTIC"
            confidence = "High"
            reasoning = [
                "Images show very high similarity",
                "Products appear to be identical",
                "Good reference for authentication"
            ]
        elif is_match and similarity_score >= 0.5:  # Lowered from 0.6
            verdict = "LIKELY AUTHENTIC"
            confidence = "Medium"
            reasoning = [
                "Images show good similarity",
                "Products appear to be the same",
                "Minor differences may be due to lighting/angle"
            ]
        elif similarity_score >= 0.3:  # Lowered from 0.4
            verdict = "NEEDS VERIFICATION"
            confidence = "Low"
            reasoning = [
                "Some similarities found but limited",
                "Compare physical details carefully",
                "Check authentication certificates"
            ]
        else:
            verdict = "SUSPICIOUS"
            confidence = "High"
            reasoning = [
                "No significant similarities found",
                "Higher risk of counterfeit",
                "Verify with official brand website"
            ]
        
        return {
            "verdict": verdict,
            "confidence": confidence,
            "similarity_score": similarity_score,
            "reasoning": reasoning,
            "recommended_actions": self._get_recommended_actions(verdict, similarity_score)
        }
    
    def _get_recommended_actions(self, verdict: str, similarity_score: float) -> list:
        """Get recommended actions based on verdict and similarity score."""
        if verdict == "LIKELY AUTHENTIC":
            return [
                "Use as reference for authentication",
                "Compare with official product images",
                "Verify serial numbers and markings"
            ]
        elif verdict == "NEEDS VERIFICATION":
            return [
                "Check for differences in brand markings",
                "Compare color variations carefully",
                "Examine quality details and stitching",
                "Verify with official brand website"
            ]
        else:  # SUSPICIOUS
            return [
                "Verify with official brand website",
                "Check for authentication certificates",
                "Compare with known authentic examples",
                "Consider professional authentication"
            ]
