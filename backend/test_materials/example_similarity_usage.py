#!/usr/bin/env python3
"""
Clean example usage of the Image Similarity Calculator
"""

import os
import sys
sys.path.append('..')

from image_similarity_scores import ImageSimilarityCalculator, ComparisonAnalyzer, SimilarityConfig

def basic_usage_example():
    """Basic usage of the similarity calculator."""
    print("🔍 Basic Similarity Calculator Usage")
    print("="*50)
    
    # Initialize the calculator
    calculator = ImageSimilarityCalculator()
    
    # Example image paths (replace with your actual paths)
    image1 = "/path/to/first/image.jpg"
    image2 = "/path/to/second/image.jpg"
    
    # Calculate similarity
    similarity_score = calculator.calculate_similarity(image1, image2)
    
    print(f"Similarity Score: {similarity_score:.3f}")
    print(f"Match Status: {'MATCH' if similarity_score >= 0.7 else 'NO MATCH'}")

def comprehensive_analysis_example():
    """Comprehensive analysis with detailed results."""
    print("\n🔍 Comprehensive Analysis Usage")
    print("="*50)
    
    # Initialize the analyzer
    analyzer = ComparisonAnalyzer()
    
    # Example image paths
    image1 = "/path/to/first/image.jpg"
    image2 = "/path/to/second/image.jpg"
    
    # Get comprehensive analysis
    result = analyzer.compare_images(image1, image2, threshold=0.7)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    # Display results
    print(f"Similarity Score: {result['similarity_score']}")
    print(f"Match Status: {result['match_status']}")
    print(f"Confidence: {result['analysis']['confidence']}")
    print(f"Recommendation: {result['analysis']['recommendation']}")
    
    # Get counterfeit detection insights
    counterfeit_insights = analyzer.get_counterfeit_detection_insights(result)
    print(f"Counterfeit Verdict: {counterfeit_insights['verdict']}")

def custom_configuration_example():
    """Using custom configuration for specific use cases."""
    print("\n🔍 Custom Configuration Usage")
    print("="*50)
    
    # Create custom configuration
    custom_config = SimilarityConfig(
        COLOR_WEIGHT=0.5,      # Increase color importance
        SIFT_WEIGHT=0.3,       # Increase feature matching
        SSIM_WEIGHT=0.1,       # Decrease structural similarity
        EDGE_WEIGHT=0.05,      # Decrease edge importance
        SHAPE_WEIGHT=0.05,     # Decrease shape importance
        DEFAULT_MATCH_THRESHOLD=0.6  # Lower threshold
    )
    
    # Initialize with custom config
    calculator = ImageSimilarityCalculator(custom_config)
    analyzer = ComparisonAnalyzer(custom_config)
    
    # Use with custom configuration
    image1 = "/path/to/first/image.jpg"
    image2 = "/path/to/second/image.jpg"
    
    similarity_score = calculator.calculate_similarity(image1, image2)
    print(f"Custom Config Similarity: {similarity_score:.3f}")

def real_world_example():
    """Real-world example with actual image paths."""
    print("\n🔍 Real-World Example")
    print("="*50)
    
    # Check if test images exist
    test_image1 = "lv.png"  # Assuming this exists in test_materials
    test_image2 = "dog.png"  # Assuming this exists in test_materials
    
    if not os.path.exists(test_image1) or not os.path.exists(test_image2):
        print("⚠️  Test images not found. Please provide valid image paths.")
        return
    
    analyzer = ComparisonAnalyzer()
    
    # Compare the images
    result = analyzer.compare_images(test_image1, test_image2)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    # Display comprehensive results
    print(f"📊 Similarity Analysis Results:")
    print(f"Score: {result['similarity_score']}")
    print(f"Status: {result['match_status']}")
    print(f"Confidence: {result['analysis']['confidence']}")
    print(f"Interpretation: {result['analysis']['interpretation']}")
    print(f"Recommendation: {result['analysis']['recommendation']}")
    print(f"Counterfeit Risk: {result['analysis']['counterfeit_risk']}")
    
    # Get counterfeit detection insights
    counterfeit_insights = analyzer.get_counterfeit_detection_insights(result)
    print(f"\n🛡️  Counterfeit Detection:")
    print(f"Verdict: {counterfeit_insights['verdict']}")
    print(f"Confidence: {counterfeit_insights['confidence']}")

def main():
    """Main function demonstrating all usage patterns."""
    print("🔍 Image Similarity Calculator Usage Examples")
    print("="*60)
    
    print("\nChoose an example to run:")
    print("1. Basic usage")
    print("2. Comprehensive analysis")
    print("3. Custom configuration")
    print("4. Real-world example")
    print("5. Run all examples")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        basic_usage_example()
    elif choice == "2":
        comprehensive_analysis_example()
    elif choice == "3":
        custom_configuration_example()
    elif choice == "4":
        real_world_example()
    elif choice == "5":
        basic_usage_example()
        comprehensive_analysis_example()
        custom_configuration_example()
        real_world_example()
    else:
        print("Invalid choice. Running real-world example...")
        real_world_example()

if __name__ == "__main__":
    main()
