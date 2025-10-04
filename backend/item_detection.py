import os
from pathlib import Path
from google import genai
from PIL import Image
from dotenv import load_dotenv
import json
from typing import Dict, Optional, List
from prompts.item_detection import get_image_analysis_prompt, get_price_search_prompt
from llm_parser import parse_json_object, parse_json_list

load_dotenv()

def analyze_image(image_path: str, allow_repositioning: bool = True) -> Dict:
    """
    Analyze an image to detect what it contains (person, product, text, or other).
    
    Args:
        image_path: Path to the image file
        allow_repositioning: Whether to allow repositioning suggestions
        
    Returns:
        Dict with structure:
        {
            "type": "person" | "product" | "text" | "other",
            "name": str,
            "confidence": "High" | "Medium" | "Low",
            "description": str,
            "needs_repositioning": bool (optional),
            "repositioning_instructions": str (optional)
        }
    """
    try:
        # Check if image exists
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Get Gemini client
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        client = genai.Client(api_key=api_key)
        
        # Get analysis prompt
        prompt = get_image_analysis_prompt(allow_repositioning)
        
        # Load and analyze image
        image = Image.open(image_path)
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=[prompt, image]
        )
        
        # Parse JSON response
        response_text = response.text.strip()
        if response_text.startswith("```"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        result = json.loads(response_text)
        
        return result
        
    except Exception as e:
        return {
            "type": "other",
            "name": "Unknown",
            "confidence": "Low",
            "description": f"Error analyzing image: {str(e)}",
            "needs_repositioning": False
        }


def get_price(product_name: str) -> List[float]:
    """
    Get the price range of an item using Gemini with web search.
    
    Args:
        product_name: Full name of the product (e.g., "Nike Air Jordan 1 Retro High OG")
        
    Returns:
        List[float]: [lower_price, upper_price] in USD
            Returns [0, 0] if price information cannot be found
            
    Example:
        >>> price_range = get_price("Apple iPhone 15 Pro Max 256GB")
        >>> print(price_range)
        [1199.0, 1299.0]
    """
    try:
        from google.genai import types
        
        # Get Gemini API key
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not found in environment variables")
            return [0, 0]
        
        # Create Gemini client
        client = genai.Client(api_key=api_key)
        
        # Get prompt for price search
        prompt = get_price_search_prompt(product_name)
        
        # Configure with Google Search tool
        tools = [
            types.Tool(googleSearch=types.GoogleSearch())
        ]
        
        # Configure generation with tools
        generate_content_config = types.GenerateContentConfig(
            tools=tools,
            thinking_config=types.ThinkingConfig(
                thinking_budget=0,
            )
        )
        
        # Create content
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]

        # Call Gemini Flash Lite model with search
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=contents,
            config=generate_content_config
        )
        
        response_text = response.text

        # Parse JSON response
        result = parse_json_object(response_text)
        
        # Extract min and max prices
        min_price = float(result.get("min_price", 0))
        max_price = float(result.get("max_price", 0))
        
        return [min_price, max_price]
        
    except json.JSONDecodeError as e:
        print(f"Error parsing price information: {str(e)}")
        return [0, 0]
    except Exception as e:
        print(f"Error fetching price: {str(e)}")
        return [0, 0]


if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("Testing get_price function")
    print("=" * 60)
    
    # Test with a sample product
    product_name = "Apple iPhone 15 Pro Max 256GB"
    print(f"\nSearching for price of: {product_name}")
    print("-" * 60)
    
    price_range = get_price(product_name)
    
    print(f"\nPrice Range (USD): {price_range}")
    print(f"Lower Price: ${price_range[0]}")
    print(f"Upper Price: ${price_range[1]}")
    
    print("\n" + "=" * 60)
