# Image Similarity Scores Package

A comprehensive system for calculating semantic similarity between product images using multiple computer vision techniques. This package is designed for counterfeit detection and product authentication.

## Features

- **Multiple Similarity Metrics**: SIFT feature matching, color histogram analysis, structural similarity (SSIM), edge detection, and shape analysis
- **Configurable Weights**: Customize the importance of different similarity metrics
- **Comprehensive Analysis**: Detailed similarity analysis with confidence levels and counterfeit detection insights
- **Batch Processing**: Compare multiple image pairs efficiently
- **Modular Design**: Clean, organized code structure with separate feature extractors

## Installation

```bash
pip install opencv-python numpy scikit-image
```

## Quick Start

### Basic Usage

```python
from image_similarity_scores import ImageSimilarityCalculator

# Initialize calculator
calculator = ImageSimilarityCalculator()

# Calculate similarity between two images
similarity_score = calculator.calculate_similarity("image1.jpg", "image2.jpg")
print(f"Similarity: {similarity_score:.3f}")
```

### Comprehensive Analysis

```python
from image_similarity_scores import ComparisonAnalyzer

# Initialize analyzer
analyzer = ComparisonAnalyzer()

# Get comprehensive analysis
result = analyzer.compare_images("image1.jpg", "image2.jpg", threshold=0.7)

print(f"Similarity Score: {result['similarity_score']}")
print(f"Match Status: {result['match_status']}")
print(f"Confidence: {result['analysis']['confidence']}")
print(f"Recommendation: {result['analysis']['recommendation']}")
```

### Custom Configuration

```python
from image_similarity_scores import SimilarityConfig, ImageSimilarityCalculator

# Create custom configuration
config = SimilarityConfig(
    COLOR_WEIGHT=0.5,      # Increase color importance
    SIFT_WEIGHT=0.3,       # Increase feature matching
    SSIM_WEIGHT=0.1,       # Decrease structural similarity
    EDGE_WEIGHT=0.05,      # Decrease edge importance
    SHAPE_WEIGHT=0.05,     # Decrease shape importance
    DEFAULT_MATCH_THRESHOLD=0.6  # Lower threshold
)

# Use with custom configuration
calculator = ImageSimilarityCalculator(config)
similarity_score = calculator.calculate_similarity("image1.jpg", "image2.jpg")
```

## API Reference

### ImageSimilarityCalculator

Main class for calculating image similarity.

#### Methods

- `calculate_similarity(image_path1, image_path2) -> float`
  - Calculate similarity between two images
  - Returns score between 0.0 and 1.0 (1.0 = identical)

- `get_detailed_analysis(image_path1, image_path2) -> Dict`
  - Get detailed analysis with individual scores and metadata

### ComparisonAnalyzer

High-level analyzer for comprehensive image comparison.

#### Methods

- `compare_images(image_path1, image_path2, threshold=None) -> Dict`
  - Compare two images with comprehensive analysis
  - Returns detailed results including match status, confidence, and recommendations

- `batch_compare(image_pairs, threshold=None) -> Dict`
  - Compare multiple image pairs in batch
  - Returns summary statistics and individual results

- `get_counterfeit_detection_insights(comparison_result) -> Dict`
  - Get specific insights for counterfeit detection
  - Returns verdict, confidence, reasoning, and recommended actions

### SimilarityConfig

Configuration class for customizing similarity calculations.

#### Parameters

- `COLOR_WEIGHT`: Weight for color histogram comparison (default: 0.35)
- `SIFT_WEIGHT`: Weight for SIFT feature matching (default: 0.25)
- `SSIM_WEIGHT`: Weight for structural similarity (default: 0.20)
- `EDGE_WEIGHT`: Weight for edge detection (default: 0.15)
- `SHAPE_WEIGHT`: Weight for shape analysis (default: 0.05)
- `DEFAULT_MATCH_THRESHOLD`: Default threshold for match determination (default: 0.7)

## Similarity Metrics

### 1. Color Histogram Comparison (35% weight)
- Compares color distributions across BGR channels
- Most reliable for similar products with consistent colors
- Uses correlation coefficient for comparison

### 2. SIFT Feature Matching (25% weight)
- Detects and matches keypoints between images
- Robust to rotation, scale, and lighting changes
- Uses multiple matching strategies (FLANN, Brute Force, distance-based)

### 3. Structural Similarity (20% weight)
- Compares structural information between images
- Uses template matching as SSIM approximation
- Good for detecting structural differences

### 4. Edge Detection (15% weight)
- Compares edge patterns and contours
- Uses adaptive Canny edge detection
- Multiple comparison methods (template matching, histogram, density)

### 5. Shape Analysis (5% weight)
- Analyzes shape characteristics using Hu moments
- Compares contour-based shape features
- Useful for detecting shape differences

## Counterfeit Detection

The system provides specialized counterfeit detection insights:

### Verdicts
- **LIKELY AUTHENTIC**: High similarity, likely same product
- **NEEDS VERIFICATION**: Some similarities, requires careful examination
- **SUSPICIOUS**: Low similarity, higher risk of counterfeit

### Confidence Levels
- **High**: Similarity score ≥ 0.8
- **Medium**: Similarity score ≥ 0.5
- **Low**: Similarity score < 0.5

### Recommended Actions
- Use as reference for authentication
- Compare with official product images
- Verify serial numbers and markings
- Check for differences in brand markings
- Verify with official brand website

## Example Output

```
🔍 Image Similarity Analysis:
   Color: 0.994 (weight: 0.35)
   SIFT: 0.923 (weight: 0.25)
   SSIM: 0.763 (weight: 0.20)
   Edge: 0.996 (weight: 0.15)
   Shape: 1.000 (weight: 0.05)
   Final Score: 0.931

✅ Comprehensive Analysis Complete!
📊 Similarity Score: 0.931
🎯 Match Status: MATCH
📏 Threshold: 0.7
🧠 Confidence: High
🛡️  Verdict: LIKELY AUTHENTIC
```

## Error Handling

The system includes robust error handling:
- File existence validation
- Image loading error handling
- Graceful fallback for missing dependencies
- Detailed error messages for debugging

## Performance Considerations

- Images are automatically resized to 400x400 for comparison
- SIFT features are limited to 1000 keypoints for performance
- Batch processing is optimized for multiple comparisons
- Memory usage is optimized for large-scale processing

## Dependencies

- OpenCV (cv2): Image processing and computer vision
- NumPy: Numerical operations
- scikit-image: Additional image processing utilities
- PIL (Pillow): Image loading and basic operations

## License

This package is part of the Counterfeit Detection System and follows the same license terms.
