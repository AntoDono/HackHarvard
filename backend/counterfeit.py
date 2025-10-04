import os
from typing import List, Dict, Any
from pathlib import Path
from google import genai
from PIL import Image
from dotenv import load_dotenv
from prompts.counterfeit import get_single_criterion_prompt
from llm_parser import parse_json_object
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

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


def analyze_single_criterion(item: str, criterion: str, criterion_number: int, total_criteria: int, image: Image.Image) -> str:
    """Send a single image and criterion to Gemini for authentication analysis."""
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    prompt = get_single_criterion_prompt(item, criterion, criterion_number, total_criteria)
    
    # Create content with prompt and single image
    contents = [prompt, image]
    
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=contents,
        config={
            "temperature": 0.1
        }
    )
    
    return response.text

def parse_results(response_text: str) -> Dict[str, Any]:
    """Parse the JSON response from Gemini and ensure all values are JSON-serializable."""
    result = parse_json_object(response_text)
    return sanitize_for_json(result)

def analyze_single_criterion_with_retry(item: str, criterion: str, criterion_number: int, 
                                       total_criteria: int, image: Image.Image, 
                                       max_retries: int = 3) -> Dict[str, Any]:
    """
    Analyze a single criterion with retry logic.
    This function is designed to be run in parallel.
    """
    print(f"\n  📋 Criterion {criterion_number}/{total_criteria}: {criterion[:50]}...")
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"    🔄 Retry attempt {attempt + 1}/{max_retries} for criterion {criterion_number}...")
            
            # Analyze this single criterion with its image
            response_text = analyze_single_criterion(item, criterion, criterion_number, total_criteria, image)
            criterion_result = parse_results(response_text)
            
            # Add confidence percentage if not present
            if 'confidence_percentage' not in criterion_result and 'score' in criterion_result:
                criterion_result['confidence_percentage'] = (criterion_result['score'] / 5.0) * 100
                criterion_result['confidence'] = criterion_result['score'] / 5.0
            
            # Success!
            score = criterion_result.get('score', 0)
            passed = criterion_result.get('passed', False)
            status = "✅" if passed else "❌"
            print(f"    {status} Criterion {criterion_number} Score: {score}/5")
            return criterion_result
            
        except (TypeError, ValueError, KeyError) as e:
            # JSON serialization or parsing errors - retry
            last_error = e
            error_msg = str(e)
            print(f"    ⚠️  Criterion {criterion_number} attempt {attempt + 1} failed: {error_msg}")
            
            if attempt == max_retries - 1:
                # Final attempt failed
                print(f"    ❌ All {max_retries} attempts failed for criterion {criterion_number}")
                return sanitize_for_json({
                    "criterion": str(criterion),
                    "score": 1,
                    "passed": False,
                    "notes": f"Error during analysis after {max_retries} attempts: {error_msg}",
                    "confidence_percentage": 20.0,
                    "confidence": 0.2,
                    "visual_markers": [],
                    "comparison_notes": "Analysis failed"
                })
                
        except Exception as e:
            # Other unexpected errors - don't retry
            last_error = e
            print(f"    ❌ Unexpected error analyzing criterion {criterion_number}: {str(e)}")
            return sanitize_for_json({
                "criterion": str(criterion),
                "score": 1,
                "passed": False,
                "notes": f"Unexpected error during analysis: {str(e)}",
                "confidence_percentage": 20.0,
                "confidence": 0.2,
                "visual_markers": [],
                "comparison_notes": "Analysis failed"
            })
    
    # Should never reach here, but just in case
    return sanitize_for_json({
        "criterion": str(criterion),
        "score": 1,
        "passed": False,
        "notes": "Analysis failed",
        "confidence_percentage": 20.0,
        "confidence": 0.2,
        "visual_markers": [],
        "comparison_notes": "Analysis failed"
    })

def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively convert numpy types and other non-serializable types to native Python types.
    """
    if isinstance(obj, dict):
        return {key: sanitize_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif obj is None or isinstance(obj, (str, int, float)):
        return obj
    else:
        # For any other type, try to convert to string
        return str(obj)

def counterfeit(item: str, criteria_data: Dict[str, List[str]], images: List[str]) -> Dict[str, Any]:
    """
    Detect if an item is counterfeit based on images and criteria using Gemini Flash Lite scoring.
    Analyzes ONE criterion per image.
    
    Args:
        item: The item name/type being authenticated
        criteria_data: Dict with 'criteria' and 'location_angle' keys
        images: List of image paths to analyze (first one is skipped as it's the initial detection image)
        
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
        return sanitize_for_json({
            "is_authentic": False,
            "overall_confidence": 0.0,
            "criteria_results": [],
            "summary": "Error: No criteria provided"
        })
    
    # Load images
    loaded_images = load_images(images)
    
    if not loaded_images:
        return sanitize_for_json({
            "is_authentic": False,
            "overall_confidence": 0.0,
            "criteria_results": [],
            "summary": "Error: No valid images provided"
        })
    
    # Skip the first image (initial detection image) and analyze criteria images
    criteria_images = loaded_images[1:] if len(loaded_images) > 1 else loaded_images
    
    # Ensure we have enough images for criteria
    if len(criteria_images) < len(criteria):
        print(f"⚠️  Warning: {len(criteria)} criteria but only {len(criteria_images)} images. Some criteria may not be properly analyzed.")
    
    print(f"\n🚀 Analyzing {len(criteria)} criteria in parallel...")
    
    # Prepare tasks for parallel execution
    tasks = []
    for i, criterion in enumerate(criteria):
        # Get the corresponding image (cycle if not enough images)
        image_idx = i % len(criteria_images)
        current_image = criteria_images[image_idx]
        tasks.append((item, criterion, i+1, len(criteria), current_image))
    
    # Run analyses in parallel using ThreadPoolExecutor
    criteria_results = []
    with ThreadPoolExecutor(max_workers=len(criteria)) as executor:
        # Submit all tasks
        future_to_criterion = {
            executor.submit(analyze_single_criterion_with_retry, *task): task[2]  # task[2] is criterion_number
            for task in tasks
        }
        
        # Collect results as they complete
        results_dict = {}
        for future in as_completed(future_to_criterion):
            criterion_number = future_to_criterion[future]
            try:
                result = future.result()
                results_dict[criterion_number] = result
            except Exception as e:
                print(f"    ❌ Thread error for criterion {criterion_number}: {str(e)}")
                results_dict[criterion_number] = sanitize_for_json({
                    "criterion": str(tasks[criterion_number - 1][1]),
                    "score": 1,
                    "passed": False,
                    "notes": f"Thread execution error: {str(e)}",
                    "confidence_percentage": 20.0,
                    "confidence": 0.2,
                    "visual_markers": [],
                    "comparison_notes": "Analysis failed"
                })
    
    # Sort results by criterion number to maintain order
    criteria_results = [results_dict[i+1] for i in range(len(criteria))]
    
    print(f"\n✅ Parallel analysis complete!")
    
    # Calculate overall metrics
    if criteria_results:
        scores = [cr.get('score', 0) for cr in criteria_results]
        avg_score = np.mean(scores)
        
        # Calculate total score percentage
        total_actual_score = sum(scores)
        total_possible_score = len(scores) * 5  # Each criterion has max 5 points
        score_percentage = (total_actual_score / total_possible_score) * 100
        overall_confidence = total_actual_score / total_possible_score
        
        passed_count = sum(1 for cr in criteria_results if cr.get('passed', False))
        failed_count = len(criteria_results) - passed_count
        
        # Determine if authentic: score must be above 80%
        is_authentic = score_percentage > 70.0
        
        # Calculate risk assessment
        counterfeit_probability = int((1 - overall_confidence) * 100)
        if avg_score >= 4:
            risk_level = "low"
        elif avg_score >= 3:
            risk_level = "medium"
        elif avg_score >= 2:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        # Collect key concerns
        key_concerns = [
            cr.get('notes', '') 
            for cr in criteria_results 
            if not cr.get('passed', False) and cr.get('notes', '')
        ][:3]  # Top 3 concerns
        
        # Generate summary
        if is_authentic:
            summary = f"✅ Item appears AUTHENTIC. Total score: {total_actual_score}/{total_possible_score} ({score_percentage:.1f}%). {passed_count}/{len(criteria_results)} criteria passed."
        else:
            summary = f"❌ Item appears COUNTERFEIT. Total score: {total_actual_score}/{total_possible_score} ({score_percentage:.1f}%). Only {passed_count}/{len(criteria_results)} criteria passed."
        
        # Generate recommendations
        recommendations = []
        if not is_authentic:
            recommendations.append("Compare with official product images from the brand website")
            if failed_count > 0:
                recommendations.append(f"Verify the {failed_count} failed criteria with expert authentication")
            recommendations.append("Check for additional authentication markers (serial numbers, holograms, etc.)")
        else:
            recommendations.append("Item shows strong authenticity indicators")
            if failed_count > 0:
                recommendations.append(f"Note: {failed_count} criteria had minor concerns, consider secondary verification")
        
        result = {
            "is_authentic": bool(is_authentic),
            "overall_confidence": float(overall_confidence),
            "criteria_results": criteria_results,
            "summary": str(summary),
            "authentication_metrics": {
                "total_criteria_checked": int(len(criteria_results)),
                "criteria_passed": int(passed_count),
                "criteria_failed": int(failed_count),
                "average_score": float(avg_score),
                "total_actual_score": int(total_actual_score),
                "total_possible_score": int(total_possible_score),
                "score_percentage": float(score_percentage),
                "confidence_distribution": {str(i): int(scores.count(i)) for i in range(1, 6)}
            },
            "risk_assessment": {
                "counterfeit_probability": int(counterfeit_probability),
                "risk_level": str(risk_level),
                "key_concerns": key_concerns
            },
            "recommendations": recommendations
        }
        return sanitize_for_json(result)
    else:
        result = {
            "is_authentic": False,
            "overall_confidence": 0.0,
            "criteria_results": [],
            "summary": "Error: No criteria were successfully analyzed"
        }
        return sanitize_for_json(result)


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
