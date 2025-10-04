def get_person_fakeness_prompt(name: str) -> str:
    """
    Generate the prompt for researching a person's fakeness.
    
    Args:
        name: The person's name to research
        
    Returns:
        str: The formatted prompt
    """
    return f"""
# Goal
Research the person "{name}" using web search to find REAL, VERIFIABLE information about their reputation, achievements, and any controversies.

# CRITICAL RULES
1. **ONLY use REAL sources that actually exist on the web**
2. **NEVER make up or fabricate sources**
3. **If you cannot find information, say "No sources found"**
4. **Maximum 10 web searches allowed**
5. **Include BOTH positive and negative findings**

# What to Search For
NEGATIVE:
- Criminal records or legal issues
- Public controversies or scandals  
- Verified misconduct or unethical behavior
- Major public backlash or criticism
- Professional misconduct or fraud

POSITIVE:
- Notable achievements or awards
- Positive contributions to society
- Professional accomplishments
- Charitable work or community service
- Recognition or honors received

# Source Requirements
- **ONLY provide URLs you actually found during web search**
- **Each source must be a real, accessible webpage**
- **Include full URL starting with https://**
- **If unsure about a source, don't include it**

# Format
Return ONLY this JSON structure:
```json
{{
    "person_name": "{name}",
    "overall_assessment": "clean" / "minor_issues" / "moderate_concerns" / "serious_concerns",
    "fakeness_score": 0-100,
    "findings": [
        {{
            "type": "positive" / "negative",
            "category": "achievement" / "award" / "contribution" / "criminal_record" / "controversy" / "misconduct",
            "title": "Brief title",
            "date": "YYYY-MM-DD or Unknown",
            "description": "What happened",
            "severity": "low" / "medium" / "high" (for negative only),
            "source": "ACTUAL URL YOU FOUND (https://...)"
        }}
    ],
    "statistics": {{
        "total_findings": number,
        "positive_findings": number,
        "negative_findings": number,
        "verified_incidents": number,
        "date_range": "YYYY-YYYY",
        "media_mentions": number,
        "severity_breakdown": {{"high": 0, "medium": 0, "low": 0}}
    }},
    "search_metadata": {{
        "searches_performed": number,
        "sources_analyzed": number,
        "last_updated": "current timestamp"
    }},
    "summary": "Brief factual summary",
    "red_flags": ["Major concerns if any"],
    "positive_notes": ["Positive context if relevant"]
}}
```

**REMEMBER**: 
- Include BOTH positive and negative findings
- Empty findings array if nothing found
- Only REAL sources from actual web searches
- Say "No credible sources found" if you can't verify information
- Fakeness score should be based on negative findings only (0 = clean, 100 = very problematic)
"""

