import os
from typing import Dict, Any
from dotenv import load_dotenv
from google import genai
from prompts.person import get_person_fakeness_prompt
from llm_parser import parse_json_object

load_dotenv()


def create_gemini_client():
    """Create and return a Gemini client."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    return genai.Client(api_key=api_key)


def call_gemini_model(client, prompt: str) -> str:
    """
    Call Gemini model with Google Search enabled.
    
    Args:
        client: Gemini client instance
        prompt: The prompt to send
        
    Returns:
        str: The model's response text
    """
    from google.genai import types
    
    # Configure with Google Search tool
    tools = [
        types.Tool(googleSearch=types.GoogleSearch())
    ]
    
    # Configure generation with tools
    generate_content_config = types.GenerateContentConfig(
        tools=tools,
        thinking_config=types.ThinkingConfig(
            thinking_budget=2048,  # No extra thinking time needed
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
    
    # Call model with search capabilities
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=contents,
        config=generate_content_config
    )
    
    return response.text


def parse_fakeness_results(response_text: str) -> Dict[str, Any]:
    """
    Parse the JSON response from Gemini.
    
    Args:
        response_text: Raw text response from the model
        
    Returns:
        Dict: Parsed JSON object
    """
    return parse_json_object(response_text)


def research_person_fakeness(name: str) -> Dict[str, Any]:
    """
    Research a person's fakeness including crimes, records, cancellations, and online drama.
    Note: The model is instructed via prompt to limit itself to ~10 web searches.
    
    Args:
        name: The person's name to research
        
    Returns:
        Dict containing:
            - person_name: str
            - overall_assessment: str
            - fakeness_score: int (0-100)
            - findings: list of issues found
            - summary: str
            - red_flags: list of major concerns
            - positive_notes: list of positive context
    """
    try:
        # Create client
        client = create_gemini_client()
        
        # Generate prompt (includes instruction to limit to 10 searches)
        prompt = get_person_fakeness_prompt(name)
        
        # Call Gemini Flash Lite model
        print(f"Researching {name}")
        response_text = call_gemini_model(client, prompt)
        
        # Parse results
        results = parse_fakeness_results(response_text)
        
        return results
        
    except Exception as e:
        print(f"Error researching person: {str(e)}")
        return {
            "person_name": name,
            "overall_assessment": "error",
            "fakeness_score": 0,
            "findings": [],
            "summary": f"Error occurred during research: {str(e)}",
            "red_flags": [],
            "positive_notes": []
        }


if __name__ == "__main__":
    # Example usage
    person_name = "Donald Trump"
    
    print(f"Researching: {person_name}")
    print("=" * 50)
    
    result = research_person_fakeness(person_name)
    
    print("\n" + "=" * 50)
    print("RESEARCH RESULTS")
    print("=" * 50)
    print(f"Person: {result.get('person_name')}")
    print(f"Overall Assessment: {result.get('overall_assessment')}")
    print(f"Fakeness Score: {result.get('fakeness_score')}/100")
    
    print(f"\nSummary: {result.get('summary')}")
    
    findings = result.get('findings', [])
    if findings:
        print(f"\nFindings ({len(findings)} issues):")
        for i, finding in enumerate(findings, 1):
            print(f"\n{i}. {finding.get('title')}")
            print(f"   Category: {finding.get('category')}")
            print(f"   Date: {finding.get('date')}")
            print(f"   Severity: {finding.get('severity')}")
            print(f"   Verified: {finding.get('verified')}")
            print(f"   Description: {finding.get('description')}")
            print(f"   Source: {finding.get('source')}")
    
    red_flags = result.get('red_flags', [])
    if red_flags:
        print(f"\nRed Flags:")
        for flag in red_flags:
            print(f"  🚩 {flag}")
    
    positive_notes = result.get('positive_notes', [])
    if positive_notes:
        print(f"\nPositive Notes:")
        for note in positive_notes:
            print(f"  ✅ {note}")

