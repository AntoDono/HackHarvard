"""
Example usage of the deepfake detector.

Note: This requires the models/ folder to be present with trained weights.
"""

from deepfake_detector import detect_deepfake_from_path, DeepfakeDetector


def simple_example():
    """Simple one-line usage."""
    print("=" * 60)
    print("Simple Example")
    print("=" * 60)
    
    image_path = "path/to/your/image.jpg"
    
    try:
        result = detect_deepfake_from_path(image_path)
        
        if result['probability'] is not None:
            print(f"✓ Image analyzed successfully")
            print(f"  Is deepfake: {result['is_deepfake']}")
            print(f"  Confidence: {result['probability']:.2%}")
            print(f"\n  Individual model results:")
            for model, prob in result['per_model'].items():
                if prob is not None:
                    print(f"    - {model}: {prob:.2%}")
        else:
            print("✗ No models were able to analyze the image")
            
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        print("  Make sure the models/ folder exists with trained weights")
    except Exception as e:
        print(f"✗ Error: {e}")


def class_based_example():
    """Using the class interface for multiple detections."""
    print("\n" + "=" * 60)
    print("Class-Based Example (Multiple Images)")
    print("=" * 60)
    
    # Initialize detector once
    detector = DeepfakeDetector()
    
    # Analyze multiple images
    images = [
        "image1.jpg",
        "image2.jpg",
        "image3.jpg"
    ]
    
    for img_path in images:
        try:
            result = detector.detect_deepfake(img_path)
            status = "⚠️  DEEPFAKE" if result['is_deepfake'] else "✓ AUTHENTIC"
            prob = result['probability']
            
            print(f"{status} - {img_path} ({prob:.1%})")
            
        except FileNotFoundError:
            print(f"✗ File not found: {img_path}")
        except Exception as e:
            print(f"✗ Error analyzing {img_path}: {e}")


if __name__ == "__main__":
    print("\nDeepfake Detector - Example Usage\n")
    
    simple_example()
    # class_based_example()  # Uncomment to test multiple images
    
    print("\n" + "=" * 60)
    print("To use this module:")
    print("1. Ensure models/ folder exists with trained weights")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Replace 'path/to/your/image.jpg' with your actual image path")
    print("=" * 60)
