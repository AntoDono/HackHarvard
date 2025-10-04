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


class DeepfakeDetector:
    """Simple interface for deepfake detection."""
    
    def __init__(self, models_root: str = "./models", python_exe: str = "python3"):
        """
        Initialize the deepfake detector.
        
        Args:
            models_root: Path to the models directory
            python_exe: Python executable to use for running model demos
        """
        self.runner = ModelRunner(models_root=models_root, python_exe=python_exe)
        self.temp_path = "./temp/delete.jpg"
        
    def _prepare_image(self, image_path: str) -> None:
        """Copy image to expected temp location."""
        os.makedirs("./temp", exist_ok=True)
        
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
                - 'probability': Average probability across all models (0-1)
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
        
        probability = result.get('average')
        
        return {
            'is_deepfake': probability > 0.5 if probability is not None else None,
            'probability': probability,
            'per_model': result.get('per_model', {})
        }


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
    detector = DeepfakeDetector(models_root=models_root)
    return detector.detect_deepfake(image_path)
