import os
from typing import List, Dict, Any
from pathlib import Path
from google import genai
from PIL import Image
from dotenv import load_dotenv
from prompts.counterfeit import get_counterfeit_prompt
from llm_parser import parse_json_object
import numpy as np

load_dotenv()

def load_images(image_paths: List[str]) -> List[Image.Image]:
    """Load all images from paths."""
    images = []
    for path in image_paths:
        if Path(path).exists():
            images.append(Image.open(path))
        else:
            print(f"Warning: Image not found at {path}")
    return images


def analyze_authenticity(item: str, criteria: List[str], images: List[Image.Image]) -> str:
    """Send images and criteria to Gemini Flash Lite for authentication analysis with 1-5 scoring."""
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    prompt = get_counterfeit_prompt(item, criteria)
    
    # Create content with prompt and all images
    contents = [prompt] + images
    
    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=contents,
        config={
            "temperature": 0.2
        }
    )
    
    return response.text

def parse_results(response_text: str) -> Dict[str, Any]:
    """Parse the JSON response from Gemini."""
    return parse_json_object(response_text)

def compute_confidence_from_scores(results: Dict[str, Any]) -> Dict[str, Any]:
    """Convert 1-5 scores to confidence percentages and add overall confidence."""
    if 'criteria_results' in results:
        scores = []
        for criterion_result in results['criteria_results']:
            # Convert 1-5 score to 0-1 confidence (1->0.2, 5->1.0)
            score = criterion_result.get('score', 3)
            confidence = score / 5.0
            criterion_result['confidence'] = confidence
            scores.append(confidence)
        
        # Add overall confidence as average
        if scores:
            results['overall_confidence'] = float(np.mean(scores))
        else:
            results['overall_confidence'] = 0.0
    else:
        results['overall_confidence'] = 0.0
    
    return results

def counterfeit(item: str, criteria_data: Dict[str, List[str]], images: List[str]) -> Dict[str, Any]:
    """
    Detect if an item is counterfeit based on images and criteria using Gemini Flash Lite scoring.
    
    Args:
        item: The item name/type being authenticated
        criteria_data: Dict with 'criteria' and 'location_angle' keys
        images: List of image paths to analyze
        
    Returns:
        Dict containing:
            - is_authentic: bool
            - overall_confidence: float (converted from 1-5 scores)
            - criteria_results: list of criterion evaluations with scores (1-5) and confidence (0-1)
            - summary: str
    """
    # Extract just the criteria (not location_angle)
    criteria = criteria_data.get('criteria', [])
    
    if not criteria:
        return {
            "is_authentic": False,
            "overall_confidence": 0.0,
            "criteria_results": [],
            "summary": "Error: No criteria provided"
        }
    
    # Load images
    loaded_images = load_images(images)
    
    if not loaded_images:
        return {
            "is_authentic": False,
            "overall_confidence": 0.0,
            "criteria_results": [],
            "summary": "Error: No valid images provided"
        }
    
    # Analyze with Gemini Flash Lite (includes 1-5 scoring)
    print(f"\nAnalyzing {len(loaded_images)} image(s) with {len(criteria)} criteria using Gemini Flash Lite...")
    response_text = analyze_authenticity(item, criteria, loaded_images)
    
    # Parse results
    results = parse_results(response_text)
    
    # Convert 1-5 scores to confidence values and add overall confidence
    results = compute_confidence_from_scores(results)
    
    return results


if __name__ == "__main__":
    # Example usage
    from criteria import criteria
    
    item_name = "LV Baby Blue Card Holder"
    
    # Get authentication criteria
    print(f"Getting criteria for {item_name}...")
    criteria_data = criteria(item_name)
    
    # Extract criteria and locations for display
    auth_criteria = criteria_data.get('criteria', [])
    locations = criteria_data.get('location_angle', [])
    
    print(f"\nCriteria to check ({len(auth_criteria)} items):")
    for i, (criterion, location) in enumerate(zip(auth_criteria, locations), 1):
        print(f"{i}. {criterion}")
        print(f"   📍 {location}")
    
    # Analyze images - will cycle if lengths don't match
    image_paths = ["./test_materials/lv.png"]  # Can be different length than criteria
    
    print(f"\nAnalyzing {len(image_paths)} image(s) with {len(auth_criteria)} criteria...")
    result = counterfeit(item_name, criteria_data, image_paths)
    
    print("\n" + "="*50)
    print("AUTHENTICATION RESULT")
    print("="*50)
    print(f"Authentic: {result.get('is_authentic')}")
    print(f"Overall Confidence: {result.get('overall_confidence', 0):.2%}")
    print(f"\nSummary: {result.get('summary')}")
    
    print("\nCriteria Results:")
    for cr in result.get('criteria_results', []):
        status = "✓" if cr.get('passed') else "✗"
        score = cr.get('score', 0)
        confidence = cr.get('confidence', 0)
        print(f"  {status} {cr.get('criterion')}")
        print(f"    Score: {score}/5 (Confidence: {confidence:.2%})")
        print(f"    Notes: {cr.get('notes')}")
