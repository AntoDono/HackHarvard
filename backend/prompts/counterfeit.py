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

# Format
Return your analysis as a JSON object:
```json
{{
    "is_authentic": true/false,
    "criteria_results": [
        {{
            "criterion": "First criterion text",
            "passed": true/false,
            "notes": "Brief explanation of what you observed in the image and why you judged it this way"
        }},
        ...
    ],
    "summary": "Overall assessment summary explaining your verdict based on visual observations"
}}
```

# Requirements:
- Focus on qualitative visual observations from the images
- Look for actual defects: wrong colors, poor stitching, blurry logos, cheap materials, incorrect patterns
- Consider if features match what's expected (colors, patterns, materials, textures)
- Only mark as counterfeit if you see clear quality issues or wrong characteristics
- Be thorough and fair in your assessment
- Provide specific visual evidence for your decisions
"""
