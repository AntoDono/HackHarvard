import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import numpy as np
import os
from model import DeepfakeModel


class DeepfakeInference:
    """Simple inference class for deepfake detection"""
    
    def __init__(self, model_path="deepfake_model.pth"):
        """
        Initialize the inference model
        
        Args:
            model_path (str): Path to the trained model file
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.transform = None
        self.label_mapping = {}
        self.index_mapping = {}
        
        # Load the model
        self._load_model(model_path)
        self._setup_transforms()
    
    def _load_model(self, model_path):
        """Load the trained model from file"""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        print(f"Loading model from {model_path}...")
        
        # Load checkpoint
        checkpoint = torch.load(model_path, map_location=self.device)
        
        # Extract configuration and mappings
        self.config = checkpoint.get('config', {})
        self.label_mapping = checkpoint.get('label_mapping', {})
        self.index_mapping = checkpoint.get('index_mapping', {})
        
        # Initialize model
        from model import DeepfakeModel
        temp_model = DeepfakeModel(self.config)
        temp_model.initialize_model()
        
        # Load state dict
        temp_model.model.load_state_dict(checkpoint['model_state_dict'])
        self.model = temp_model.model.to(self.device)
        self.model.eval()
        
        print(f"Model loaded successfully on {self.device}")
        print(f"Label mapping: {self.label_mapping}")
        print(f"Index mapping: {self.index_mapping}")
    
    def _setup_transforms(self):
        """Setup image preprocessing transforms"""
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.ToTensor(),
            transforms.Resize((224, 224)),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def _preprocess_image(self, image_path):
        """Preprocess image for inference"""
        try:
            # Load and convert image
            img = Image.open(image_path).convert("RGB")
            img = np.array(img)
            
            # Apply transforms
            img = self.transform(img)
            img = img.unsqueeze(0)  # Add batch dimension
            img = img.to(self.device)
            
            return img
        except Exception as e:
            raise ValueError(f"Error preprocessing image {image_path}: {str(e)}")
    
    def is_deepfake(self, image_path, confidence_threshold=0.5):
        """
        Determine if an image is a deepfake
        
        Args:
            image_path (str): Path to the image file
            confidence_threshold (float): Threshold for classification (default: 0.5)
            
        Returns:
            dict: {
                'is_deepfake': bool,
                'confidence': float,
                'prediction': str,
                'probabilities': dict
            }
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Initialize the inference class first.")
        
        # Preprocess image
        img = self._preprocess_image(image_path)
        
        # Run inference
        with torch.no_grad():
            outputs = self.model(img)
            probabilities = F.softmax(outputs, dim=1)
            
            # Get prediction
            predicted_class = outputs.argmax(dim=1).item()
            confidence = probabilities[0][predicted_class].item()
            
            # Determine if it's a deepfake
            is_deepfake = predicted_class == 1  # Assuming 1 = Fake, 0 = Real
            prediction_label = self.index_mapping.get(predicted_class, "Unknown")
            
            # Get all probabilities
            prob_dict = {}
            for idx, prob in enumerate(probabilities[0]):
                label = self.index_mapping.get(idx, f"Class_{idx}")
                prob_dict[label] = prob.item()
        
        return {
            'is_deepfake': is_deepfake,
            'confidence': confidence,
            'prediction': prediction_label,
            'probabilities': prob_dict,
            'raw_confidence': confidence if is_deepfake else 1.0 - confidence
        }
    
    def predict_batch(self, image_paths, confidence_threshold=0.5):
        """
        Predict on multiple images
        
        Args:
            image_paths (list): List of image file paths
            confidence_threshold (float): Threshold for classification
            
        Returns:
            list: List of prediction results for each image
        """
        results = []
        
        for image_path in image_paths:
            try:
                result = self.is_deepfake(image_path, confidence_threshold)
                result['image_path'] = image_path
                result['success'] = True
            except Exception as e:
                result = {
                    'image_path': image_path,
                    'success': False,
                    'error': str(e)
                }
            
            results.append(result)
        
        return results


# Convenience function for simple usage
def is_deepfake(image_path, model_path="deepfake_model.pth", confidence_threshold=0.5):
    """
    Simple function to check if an image is a deepfake
    
    Args:
        image_path (str): Path to the image file
        model_path (str): Path to the trained model file
        confidence_threshold (float): Threshold for classification
        
    Returns:
        dict: Prediction results
    """
    # Create inference instance
    inference = DeepfakeInference(model_path)
    
    # Run prediction
    return inference.is_deepfake(image_path, confidence_threshold)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python inference.py <image_path> [model_path]")
        print("Example: python inference.py test_image.jpg deepfake_model.pth")
        sys.exit(1)
    
    image_path = sys.argv[1]
    model_path = sys.argv[2] if len(sys.argv) > 2 else "deepfake_model.pth"
    
    try:
        # Run inference
        result = is_deepfake(image_path, model_path)
        
        print(f"\n🔍 Deepfake Detection Results:")
        print(f"Image: {image_path}")
        print(f"Prediction: {result['prediction']}")
        print(f"Is Deepfake: {result['is_deepfake']}")
        print(f"Confidence: {result['confidence']:.4f}")
        print(f"Raw Confidence: {result['raw_confidence']:.4f}")
        print(f"\n📊 Probabilities:")
        for label, prob in result['probabilities'].items():
            print(f"  {label}: {prob:.4f}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
