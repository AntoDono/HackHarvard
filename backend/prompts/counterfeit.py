def get_counterfeit_prompt(item: str, criteria: list) -> str:
    """
    Generate the prompt for counterfeit detection.
    
    Args:
        item: The item name/type being authenticated
        criteria: List of authentication criteria to check
        
    Returns:
        str: The formatted prompt
    """
    # Build criteria text
    criteria_text = []
    for i, criterion in enumerate(criteria, 1):
        criteria_text.append(f"{i}. {criterion}")
    criteria_formatted = "\n".join(criteria_text)
    
    return f"""
# Goal
You are an expert authenticator analyzing images of a {item} to determine if it is authentic or counterfeit.

# Criteria to Check
Carefully examine the images against these specific authentication criteria:

{criteria_formatted}

# Task
Based on the images and your expert visual analysis, evaluate whether the item is authentic or counterfeit.
For EACH criterion, provide a confidence score from 1-5:
- 5: Clearly authentic, matches expected quality perfectly
- 4: Likely authentic, minor concerns but acceptable
- 3: Uncertain, could go either way
- 2: Likely counterfeit, notable quality issues
- 1: Clearly counterfeit, obvious defects or wrong characteristics

# Format
Return your analysis as a JSON object:
```json
{{
    "is_authentic": true/false,
    "criteria_results": [
        {{
            "criterion": "First criterion text",
            "score": 1-5,
            "passed": true/false,
            "notes": "Brief explanation of what you observed in the image and why you gave this score",
            "confidence_percentage": 0-100,
            "visual_markers": ["marker1", "marker2"],
            "comparison_notes": "How it compares to authentic versions"
        }},
        ...
    ],
    "authentication_metrics": {{
        "total_criteria_checked": number,
        "criteria_passed": number,
        "criteria_failed": number,
        "average_score": number,
        "confidence_distribution": {{"1": X, "2": Y, "3": Z, "4": A, "5": B}}
    }},
    "risk_assessment": {{
        "counterfeit_probability": 0-100,
        "risk_level": "low" / "medium" / "high" / "critical",
        "key_concerns": ["concern1", "concern2"]
    }},
    "summary": "Overall assessment summary explaining your verdict based on visual observations",
    "recommendations": ["Specific recommendations for further verification"]
}}
```

# Requirements:
- Focus on qualitative visual observations from the images
- Look for actual defects: wrong colors, poor stitching, blurry logos, cheap materials, incorrect patterns
- Consider if features match what's expected (colors, patterns, materials, textures)
- Give objective scores based on what you can actually see
- Provide specific visual evidence for your scores
- Be thorough and fair in your assessment
"""
