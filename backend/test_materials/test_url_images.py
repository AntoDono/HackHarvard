#!/usr/bin/env python3
"""
Clean test script for comparing images from URLs
"""

import os
import sys
import requests
import tempfile
from urllib.parse import urlparse
sys.path.append('..')

from image_similarity_scores import ImageSimilarityCalculator, ComparisonAnalyzer, SimilarityConfig

def download_image_from_url(url: str, temp_dir: str) -> str:
    """Download an image from URL and save it to a temporary file."""
    try:
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL format")
        
        # Download the image
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Determine file extension
        content_type = response.headers.get('content-type', '')
        if 'jpeg' in content_type or 'jpg' in content_type:
            ext = '.jpg'
        elif 'png' in content_type:
            ext = '.png'
        elif 'webp' in content_type:
            ext = '.webp'
        else:
            ext = '.jpg'
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext, dir=temp_dir, mode='wb')
        temp_file.write(response.content)
        temp_file.close()
        
        # Verify the image can be loaded by OpenCV
        import cv2
        test_img = cv2.imread(temp_file.name)
        if test_img is None:
            # Try to convert using PIL
            from PIL import Image
            try:
                pil_img = Image.open(temp_file.name)
                if pil_img.mode != 'RGB':
                    pil_img = pil_img.convert('RGB')
                jpeg_path = temp_file.name.replace(ext, '.jpg')
                pil_img.save(jpeg_path, 'JPEG')
                test_img = cv2.imread(jpeg_path)
                if test_img is not None:
                    return jpeg_path
            except:
                pass
            return None
        
        return temp_file.name
        
    except Exception as e:
        return None

def test_url_images():
    """Test similarity calculation with images from URLs."""
    
    print("🔍 URL Image Similarity Test")
    print("="*50)
    
    # Get URLs from user
    print("\nEnter URLs to two images to compare:")
    url1 = input("First image URL: ").strip()
    url2 = input("Second image URL: ").strip()
    
    if not url1 or not url2:
        print("❌ Both image URLs are required")
        return
    
    # Create temporary directory for downloaded images
    with tempfile.TemporaryDirectory() as temp_dir:
        # Download images
        image1_path = download_image_from_url(url1, temp_dir)
        image2_path = download_image_from_url(url2, temp_dir)
        
        if not image1_path or not image2_path:
            print("❌ Failed to download images")
            return
        
        # Test comprehensive analysis
        analyzer = ComparisonAnalyzer()
        result = analyzer.compare_images(image1_path, image2_path, threshold=0.6)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        
        # Display results
        print(f"\n📊 Results:")
        print(f"Similarity Score: {result['similarity_score']}")
        print(f"Match Status: {result['match_status']}")
        print(f"Confidence: {result['analysis']['confidence']}")
        print(f"Recommendation: {result['analysis']['recommendation']}")
        
        # Get counterfeit detection insights
        counterfeit_insights = analyzer.get_counterfeit_detection_insights(result)
        if "error" not in counterfeit_insights:
            print(f"\n🛡️  Counterfeit Detection:")
            print(f"Verdict: {counterfeit_insights['verdict']}")
            print(f"Confidence: {counterfeit_insights['confidence']}")

def test_custom_config():
    """Test with custom configuration."""
    
    print("\n🔍 Custom Configuration Test")
    print("="*50)
    
    # Create custom configuration
    custom_config = SimilarityConfig(
        COLOR_WEIGHT=0.2,
        SIFT_WEIGHT=0.5,
        SSIM_WEIGHT=0.15,
        EDGE_WEIGHT=0.1,
        SHAPE_WEIGHT=0.05,
        DEFAULT_MATCH_THRESHOLD=0.55
    )
    
    # Get image paths
    print("\nEnter paths to two product images to compare:")
    image_path1 = input("First image path: ").strip()
    image_path2 = input("Second image path: ").strip()
    
    if not image_path1 or not image_path2:
        print("❌ Both image paths are required")
        return
    
    # Expand tilde and resolve paths
    image_path1 = os.path.expanduser(image_path1)
    image_path2 = os.path.expanduser(image_path2)
    
    try:
        # Test with custom configuration
        analyzer = ComparisonAnalyzer(custom_config)
        result = analyzer.compare_images(image_path1, image2_path)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        
        print(f"\n📊 Custom Configuration Results:")
        print(f"Similarity Score: {result['similarity_score']}")
        print(f"Match Status: {result['match_status']}")
        print(f"Confidence: {result['analysis']['confidence']}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

def main():
    """Main test function."""
    
    print("🔍 Image Similarity Test Suite")
    print("="*50)
    
    print("\nChoose test mode:")
    print("1. Test with image URLs")
    print("2. Test with custom configuration")
    print("3. Run both tests")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        test_url_images()
    elif choice == "2":
        test_custom_config()
    elif choice == "3":
        test_url_images()
        print("\n" + "="*50 + "\n")
        test_custom_config()
    else:
        print("Invalid choice. Starting URL test...")
        test_url_images()

if __name__ == "__main__":
    main()
