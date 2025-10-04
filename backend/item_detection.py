import os
from pathlib import Path
from google import genai
from PIL import Image
from dotenv import load_dotenv
import json
from typing import Dict

load_dotenv()

def analyze_product_from_image(image_path: str) -> Dict:
    """
    Analyze a product image and return specific format:
    - If high confidence product found: {"product": {...}}
    - If repositioning needed: {"repositioning instructions": "..."}
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dict: Either product details or repositioning instructions
    """
    try:
        # Check if image exists
        if not Path(image_path).exists():
            return {"repositioning instructions": "Image file not found. Please provide a valid image path."}
        
        # Get Gemini client
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return {"repositioning instructions": "GEMINI_API_KEY not found in environment variables."}
        
        client = genai.Client(api_key=api_key)
        
        # Compact prompt for exact product identification
        prompt = """Return ONLY valid JSON. Identify EXACT products (not generic). Use "N/A" for missing fields.

        {
          "detection_status": "success" | "needs_repositioning",
          "repositioning_request": {"needed": true/false, "instructions": "specific instructions OR N/A", "reason": "reason OR N/A"},
          "products": [{
            "name": "EXACT product name OR N/A", "brand": "Brand OR N/A", "version": "Version/size OR N/A",
            "category": "Category OR N/A", "description": "Description OR N/A", "price": "Price OR N/A",
            "barcode": "Barcode OR N/A", "ingredients": "Ingredients OR N/A", "nutritional_info": "Nutrition OR N/A",
            "size": "Size OR N/A", "color": "Color OR N/A", "material": "Material OR N/A",
            "country_of_origin": "Origin OR N/A", "expiry_date": "Expiry OR N/A",
            "confidence": "High|Medium|Low", "identification_certainty": "Percentage OR N/A"
          }],
          "image_quality": "Quality assessment", "visibility_issues": ["Issues"], "detection_notes": "Notes"
        }

        GOOD: "Coca-Cola Classic 12oz can" BAD: "soda"
        If unclear: "needs_repositioning" with instructions like "Rotate to show label" or "Hold closer"
        """
        
        # Load and analyze image
        image = Image.open(image_path)
        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=[prompt, image]
        )
        
        # Parse JSON response
        response_text = response.text.strip()
        if response_text.startswith("```"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        result = json.loads(response_text)
        
        # Validate and fill missing fields for products
        if "products" in result and result["products"]:
            required_fields = [
                "name", "brand", "version", "category", "description", "price", 
                "barcode", "ingredients", "nutritional_info", "size", "color", 
                "material", "country_of_origin", "expiry_date", "confidence", 
                "identification_certainty"
            ]
            for product in result["products"]:
                for field in required_fields:
                    if field not in product or not product[field]:
                        product[field] = "N/A"
        
        # Check detection status and confidence
        detection_status = result.get("detection_status", "success")
        products = result.get("products", [])
        
        # If repositioning is needed, return repositioning instructions
        if detection_status == "needs_repositioning":
            repo_req = result.get("repositioning_request", {})
            instructions = repo_req.get("instructions", "Please adjust the product position for better visibility")
            return {"repositioning instructions": instructions}
        
        # If no products found, return repositioning instructions
        if not products:
            return {"repositioning instructions": "No products detected. Please ensure the product is clearly visible in the image."}
        
        # Check for high confidence products
        high_confidence_products = [p for p in products if p.get("confidence") == "High"]
        
        if high_confidence_products:
            # Return the first high confidence product
            product = high_confidence_products[0]
            return {"product": product}
        else:
            # If only medium/low confidence, return repositioning instructions
            return {"repositioning instructions": "Product detected but with low confidence. Please provide a clearer image with better lighting and focus."}
        
    except json.JSONDecodeError:
        return {"repositioning instructions": "AI response was not in valid format. Please try with a clearer image."}
    except Exception as e:
        return {"repositioning instructions": f"Error analyzing image. Please ensure the image is clear and try again."}
