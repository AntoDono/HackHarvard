import os
from google import genai
from PIL import Image
from dotenv import load_dotenv
from llm_parser import parse_json_object

load_dotenv()


def analyze_other_content(image_path: str, item_name: str) -> dict:
    """
    Analyze other/general content using Gemini vision.
    
    Args:
        image_path: Path to the image file
        item_name: Detected name/description of the content
        
    Returns:
        Dict containing analysis results
    """
    try:
        # Load the image
        image = Image.open(image_path)
        
        # Create Gemini client
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        prompt = f"""
You are analyzing an image that contains: {item_name}

Please provide a comprehensive analysis of this content:

1. **What is it?** - Describe what you see in detail
2. **Context & Information** - Provide relevant background information, history, or facts
3. **Interesting Details** - Point out notable features or interesting aspects
4. **Additional Insights** - Any other relevant information that would be useful

Return your analysis as a JSON object:
```json
{{
    "title": "Brief title of what this is",
    "description": "Detailed description of what's in the image",
    "key_facts": [
        "Fact 1",
        "Fact 2",
        "Fact 3"
    ],
    "interesting_details": [
        "Detail 1",
        "Detail 2"
    ],
    "context": "Background information and context",
    "category": "Category (e.g., Architecture, Nature, Art, Object, etc.)",
    "authenticity_notes": "If applicable, notes about authenticity or notable features"
}}
```

Be informative, accurate, and engaging in your analysis.
"""
        
        # Call Gemini
        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=[prompt, image],
            config={
                "temperature": 0.3
            }
        )
        
        # Parse response
        result = parse_json_object(response.text)
        
        return result
        
    except Exception as e:
        print(f"❌ Error analyzing other content: {str(e)}")
        return {
            "title": item_name,
            "description": f"Could not analyze: {str(e)}",
            "key_facts": [],
            "interesting_details": [],
            "context": "Analysis failed",
            "category": "Unknown",
            "authenticity_notes": ""
        }


if __name__ == "__main__":
    # Test
    result = analyze_other_content("./test_materials/dog.png", "Dog")
    print(result)

