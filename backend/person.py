import os
from typing import Dict, Any
from dotenv import load_dotenv
from groq import Groq
from prompts.person import get_person_fakeness_prompt
from llm_parser import parse_json_object

load_dotenv()


def create_groq_client() -> Groq:
    """Create and return a Groq client."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    return Groq(api_key=api_key)


def call_groq_compound_model(client: Groq, prompt: str) -> str:
    """
    Call Groq's compound model with web search capabilities.
    
    Args:
        client: Groq client instance
        prompt: The prompt to send
        
    Returns:
        str: The model's response text
    """
    response = client.chat.completions.create(
        model="groq/compound",
        messages=[{"role": "user", "content": prompt}],
        compound_custom={
            "tools": {
                "enabled_tools": ["web_search", "browser_automation"]
            }
        }
    )
    return response.choices[0].message.content


def parse_fakeness_results(response_text: str) -> Dict[str, Any]:
    """
    Parse the JSON response from Groq.
    
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
        client = create_groq_client()
        
        # Generate prompt (includes instruction to limit to 10 searches)
        prompt = get_person_fakeness_prompt(name)
        
        # Call Groq compound model
        print(f"Researching {name} using Groq compound model (prompt instructs max 10 searches)...")
        response_text = call_groq_compound_model(client, prompt)
        
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
    person_name = "Elon Musk"
    
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

