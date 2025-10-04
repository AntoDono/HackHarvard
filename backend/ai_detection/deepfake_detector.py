"""
Simplified deepfake detection interface.

This module provides a simple function to detect deepfakes from image paths.
It wraps the ModelRunner class to provide an easy-to-use interface.

Note: This requires the 'models/' folder with trained model weights to function.
The models folder is not included in the base repository and must be downloaded separately.
"""

import os
from typing import Dict, Optional
from packaged_models.model_runner import ModelRunner

def calculate_weighted_average(per_model: Dict[str, Optional[float]]) -> Optional[float]:
    """
    Calculate weighted average of model predictions.
    
    Models are weighted to give more influence to the more reliable detectors:
    - faceforensics_image: 2.0x weight (specialized for face manipulation detection)
    - ganimagedetection_image: 2.0x weight (excellent for GAN-generated images)
    - cnndetection_image: 2.0x weight (robust CNN-based detector)
    - photoshop_fal_image: 1.0x weight (still useful but less emphasis)
    
    Args:
        per_model: Dictionary mapping model names to their predictions (0-1) or None
        
    Returns:
        Weighted average probability (0-1), or None if no valid predictions
        
    Example:
        >>> per_model = {
        ...     'cnndetection_image': 0.8,
        ...     'ganimagedetection_image': 0.006,
        ...     'faceforensics_image': 0.75,
        ...     'photoshop_fal_image': 0.001
        ... }
        >>> calculate_weighted_average(per_model)
        0.5877  # (0.8*2 + 0.006*2 + 0.75*2 + 0.001*1) / 7
    """
    # Define model weights (higher = more influence)
    model_weights = {
        "cnndetection_image": 2.0,  
        "ganimagedetection_image": 2.0,
        "faceforensics_image": 2.0,
        "photoshop_fal_image": 1.0,
    }
    
    weighted_sum = 0.0
    total_weight = 0.0
    
    for model_name, prediction in per_model.items():
        if prediction is not None:
            weight = model_weights.get(model_name, 1.0)  # Default weight of 1.0 for unknown models
            weighted_sum += float(prediction) * weight
            total_weight += 1
    
    if total_weight > 0:
        return round(weighted_sum / total_weight, 6)
    
    return None


class DeepfakeDetector:
    """Simple interface for deepfake detection."""
    
    def __init__(self, models_root: str = "./models", python_exe: str = "python3"):
        """
        Initialize the deepfake detector.
        
        Args:
            models_root: Path to the models directory
            python_exe: Python executable to use for running model demos
        """
        # Convert to absolute path for reliability
        models_root = os.path.abspath(models_root)
        
        # Check if models directory exists
        if not os.path.exists(models_root):
            raise FileNotFoundError(
                f"Models directory not found at: {models_root}\n"
                f"Please run 'python download_models.py' to download the required models."
            )
        
        self.runner = ModelRunner(models_root=models_root, python_exe=python_exe)
        self.models_root = models_root
        self.temp_dir = os.path.join(os.path.dirname(models_root), "temp")
        self.temp_path = os.path.join(self.temp_dir, "delete.jpg")
        
    def _prepare_image(self, image_path: str) -> None:
        """Copy image to expected temp location."""
        os.makedirs(self.temp_dir, exist_ok=True)
        
        from PIL import Image
        img = Image.open(image_path)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        # Save to temp location expected by models
        img.save(self.temp_path)
    
    def detect_deepfake(self, image_path: str, timeout: int = 90) -> Dict[str, any]:
        """
        Detect if an image is a deepfake.
        
        Args:
            image_path: Path to the image file to analyze
            timeout: Maximum time in seconds to wait for detection
            
        Returns:
            Dictionary containing:
                - 'is_deepfake': Boolean indicating if image is likely a deepfake (prob > 0.5)
                - 'probability': Weighted average probability across all models (0-1)
                - 'per_model': Dictionary of individual model probabilities
                
        Example:
            detector = DeepfakeDetector()
            result = detector.detect_deepfake("path/to/image.jpg")
            print(f"Is deepfake: {result['is_deepfake']}")
            print(f"Probability: {result['probability']:.2%}")
        """
        # Prepare image in expected location
        self._prepare_image(image_path)
        
        # Run all image detection models
        result = self.runner.run_image_ensemble(timeout=timeout)
        
        # Clean up
        if os.path.exists(self.temp_path):
            os.remove(self.temp_path)
        
        # Calculate weighted average instead of simple average
        per_model = result.get('per_model', {})
        probability = calculate_weighted_average(per_model)
        
        return {
            'is_deepfake': probability > 0.5 if probability is not None else None,
            'probability': probability,
            'per_model': per_model
        }

DETECTOR = None

def detect_deepfake_from_path(image_path: str, models_root: str = "./models") -> Dict[str, any]:
    """
    Convenience function to detect deepfakes from an image path.
    
    Args:
        image_path: Path to the image file
        models_root: Path to the models directory (default: "./models")
        
    Returns:
        Dictionary with detection results
        
    Example:
        result = detect_deepfake_from_path("suspicious_image.jpg")
        if result['is_deepfake']:
            print(f"Warning: Image is likely AI-generated ({result['probability']:.2%})")
    """
    if DETECTOR is None:
        DETECTOR = DeepfakeDetector(models_root=models_root)
    return DETECTOR.detect_deepfake(image_path)
