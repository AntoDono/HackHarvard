import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from prompts.fact_check import get_fact_check_prompt
from llm_parser import parse_json_object
from pathlib import Path
from PIL import Image

load_dotenv()


def fact_check(image_path: str):
    """
    Fact-check the content of an image using Gemini with web search.
    
    The image can contain tweets, text, infographics, drawings, or any visual content
    with factual claims. This function will:
    1. Analyze the image to extract factual claims
    2. Use web search to verify each claim
    3. Return a detailed fact-check report
    
    Args:
        image_path: Path to the image file to fact-check
    
    Returns:
        dict: A dictionary containing:
            - image_type: The type of content in the image
            - contains_factual_claims: Whether factual claims were found
            - overall_verdict: TRUE | FALSE | PARTIALLY TRUE | etc.
            - confidence_score: 0.0-1.0 confidence in the verdict
            - claims: List of individual claims with verdicts and evidence
            - summary: Brief summary of findings
            - important_notes: Any caveats or additional context
    
    Raises:
        ValueError: If GEMINI_API_KEY is not found or image doesn't exist
        FileNotFoundError: If the image file doesn't exist
    """
    # Validate image path
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Get API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    # Initialize Gemini client
    client = genai.Client(api_key=api_key)
    
    # Get the fact-check prompt
    prompt = get_fact_check_prompt()
    
    # Load the image
    print(f"Loading image for fact-checking: {image_path}")
    image = Image.open(image_path)
    
    # Configure with Google Search tool
    tools = [
        types.Tool(googleSearch=types.GoogleSearch())
    ]
    
    # Configure generation with tools
    generate_content_config = types.GenerateContentConfig(
        tools=tools,
        thinking_config=types.ThinkingConfig(
            thinking_budget=2048,
        )
    )
    
    # Create content with image and prompt
    contents = [prompt, image]
    
    # Call model with search capabilities
    print("Analyzing image and fact-checking claims...")
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=contents,
        config=generate_content_config
    )
    
    content = response.text
    
    # Parse JSON response
    fact_check_results = parse_json_object(content)
    
    return fact_check_results


if __name__ == "__main__":
    import sys
    import json
    
    # Example usage
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Default test image
        image_path = f"test_materials/fact_check.png"
        print(f"No image provided, using default: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        print("Usage: python fact_check.py <image_path>")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"FACT-CHECKING IMAGE: {image_path}")
    print(f"{'='*60}\n")
    
    try:
        results = fact_check(image_path)
        
        # Pretty print results
        print(f"Image Type: {results.get('image_type', 'Unknown')}")
        print(f"Contains Factual Claims: {results.get('contains_factual_claims', 'Unknown')}")
        print(f"Overall Verdict: {results.get('overall_verdict', 'Unknown')}")
        print(f"Confidence Score: {results.get('confidence_score', 0.0):.2f}")
        
        claims = results.get('claims', [])
        if claims:
            print(f"\n{'='*60}")
            print(f"CLAIMS ANALYZED: {len(claims)}")
            print(f"{'='*60}\n")
            
            for i, claim in enumerate(claims, 1):
                print(f"Claim {i}: {claim.get('claim_text', 'N/A')}")
                print(f"  Type: {claim.get('claim_type', 'N/A')}")
                print(f"  Verdict: {claim.get('verdict', 'N/A')}")
                print(f"  Confidence: {claim.get('confidence', 0.0):.2f}")
                print(f"  Evidence: {claim.get('evidence', 'N/A')}")
                
                sources = claim.get('sources', [])
                if sources:
                    print(f"  Sources:")
                    for source in sources:
                        print(f"    - {source.get('title', 'Unknown')} [{source.get('reliability', 'unknown')}]")
                        if source.get('url'):
                            print(f"      {source.get('url')}")
                
                if claim.get('context'):
                    print(f"  Context: {claim.get('context')}")
                print()
        
        print(f"{'='*60}")
        print(f"SUMMARY")
        print(f"{'='*60}")
        print(results.get('summary', 'N/A'))
        
        if results.get('important_notes'):
            print(f"\nImportant Notes:")
            print(results.get('important_notes'))
        
    except Exception as e:
        print(f"Error during fact-checking: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

