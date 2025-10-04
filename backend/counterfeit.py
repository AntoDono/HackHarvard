import os
from typing import List, Dict, Any
from pathlib import Path
from google import genai
from PIL import Image
from dotenv import load_dotenv
from prompts.counterfeit import get_counterfeit_prompt
from llm_parser import parse_json_object
from sentence_transformers import SentenceTransformer
import numpy as np

load_dotenv()

# Initialize CLIP model for objective scoring
clip_model = SentenceTransformer('clip-ViT-B-32')

def load_images(image_paths: List[str]) -> List[Image.Image]:
    """Load all images from paths."""
    images = []
    for path in image_paths:
        if Path(path).exists():
            images.append(Image.open(path))
        else:
            print(f"Warning: Image not found at {path}")
    return images

def compute_image_embedding(image: Image.Image):
    """Get CLIP embedding for an image."""
    return clip_model.encode(image, convert_to_tensor=False)

def compute_text_embedding(text: str):
    """Get CLIP embedding for text."""
    return clip_model.encode(text, convert_to_tensor=False)

def compute_similarity(embedding1, embedding2) -> float:
    """Calculate cosine similarity between two embeddings."""
    similarity = np.dot(embedding1, embedding2) / (
        np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
    )
    return float(similarity)

def cycle_list(lst: List, target_length: int) -> List:
    """Cycle through a list to match target length."""
    if not lst:
        return []
    result = []
    for i in range(target_length):
        result.append(lst[i % len(lst)])
    return result

def compute_scores_with_cycling(images: List[Image.Image], criteria: List[str]) -> List[float]:
    """
    Compute confidence scores, cycling through whichever list is shorter.
    If images < criteria: cycle images
    If criteria < images: cycle criteria
    
    Returns list of scores for each position.
    """
    num_images = len(images)
    num_criteria = len(criteria)
    
    # Cycle whichever is shorter
    if num_images < num_criteria:
        print(f"  Cycling {num_images} images to match {num_criteria} criteria")
        cycled_images = cycle_list(images, num_criteria)
        cycled_criteria = criteria
    elif num_criteria < num_images:
        print(f"  Cycling {num_criteria} criteria to match {num_images} images")
        cycled_images = images
        cycled_criteria = cycle_list(criteria, num_images)
    else:
        # Equal length, no cycling needed
        cycled_images = images
        cycled_criteria = criteria
    
    # Compute scores
    scores = []
    for i, (image, criterion) in enumerate(zip(cycled_images, cycled_criteria)):
        print(f"  Scoring pair {i+1}/{len(cycled_images)}...")
        
        # Get embeddings - use raw criteria text
        image_embedding = compute_image_embedding(image)
        criterion_embedding = compute_text_embedding(criterion)
        
        # Compute similarity
        score = compute_similarity(image_embedding, criterion_embedding)
        scores.append(score)
    
    return scores

def analyze_authenticity(item: str, criteria: List[str], images: List[Image.Image]) -> str:
    """Send images and criteria to Gemini for authentication analysis."""
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    # Don't pass scores to LLM
    prompt = get_counterfeit_prompt(item, criteria)
    
    # Create content with prompt and all images
    contents = [prompt] + images
    
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=contents,
        config={
            "temperature": 0.2
        }
    )
    
    return response.text

def parse_results(response_text: str) -> Dict[str, Any]:
    """Parse the JSON response from Gemini."""
    return parse_json_object(response_text)

def add_scores_to_results(results: Dict[str, Any], scores: List[float]) -> Dict[str, Any]:
    """Add CLIP scores to the results."""
    # Add overall confidence as average of all scores
    results['overall_confidence'] = float(np.mean(scores))
    
    # Add individual scores to each criterion result
    if 'criteria_results' in results:
        for i, criterion_result in enumerate(results['criteria_results']):
            if i < len(scores):
                criterion_result['confidence'] = scores[i]
    
    return results

def counterfeit(item: str, criteria_data: Dict[str, List[str]], images: List[str]) -> Dict[str, Any]:
    """
    Detect if an item is counterfeit based on images and criteria.
    Cycles through whichever list is shorter (images or criteria).
    
    Args:
        item: The item name/type being authenticated
        criteria_data: Dict with 'criteria' and 'location_angle' keys
        images: List of image paths to analyze
        
    Returns:
        Dict containing:
            - is_authentic: bool
            - overall_confidence: float (CLIP-based)
            - criteria_results: list of criterion evaluations with confidence scores
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
    
    # Compute CLIP-based confidence scores (with cycling)
    print(f"Computing CLIP confidence scores ({len(loaded_images)} images vs {len(criteria)} criteria)...")
    clip_scores = compute_scores_with_cycling(loaded_images, criteria)
    
    # Print scores
    print("\nCLIP Similarity Scores:")
    for i, score in enumerate(clip_scores):
        print(f"  Pair {i+1}: {score:.3f}")
    
    # Analyze with Gemini (for qualitative assessment - no scores passed)
    print("\nAnalyzing with Gemini...")
    response_text = analyze_authenticity(item, criteria, loaded_images)
    
    # Parse results
    results = parse_results(response_text)
    
    # Add CLIP scores to results
    results = add_scores_to_results(results, clip_scores)
    
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
    
    print(f"\nAnalyzing {len(image_paths)} image(s) vs {len(auth_criteria)} criteria...")
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
        confidence = cr.get('confidence', 0)
        print(f"  {status} {cr.get('criterion')}")
        print(f"    Confidence: {confidence:.2%}")
        print(f"    Notes: {cr.get('notes')}")
