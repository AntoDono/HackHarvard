def get_single_criterion_prompt(item: str, criterion: str, criterion_number: int, total_criteria: int) -> str:
    """
    Generate the prompt for analyzing a single criterion with a single image.
    
    Args:
        item: The item name/type being authenticated
        criterion: The specific authentication criterion to check
        criterion_number: The number of this criterion (1-indexed)
        total_criteria: Total number of criteria
        
    Returns:
        str: The formatted prompt
    """
    return f"""
# Goal
You are an expert authenticator analyzing an image of a {item} to verify a SPECIFIC authentication criterion.

# Criterion to Verify (#{criterion_number} of {total_criteria})
Focus ONLY on this specific authentication criterion:

**{criterion}**

# Task
Based on the provided image and your expert visual analysis, evaluate this ONE criterion.
Provide a confidence score from 1-5:
- 5: Clearly authentic, matches expected quality perfectly
- 4: Likely authentic, minor concerns but acceptable
- 3: Uncertain, could go either way
- 2: Likely counterfeit, notable quality issues
- 1: Clearly counterfeit, obvious defects or wrong characteristics

# Format
Return your analysis as a JSON object:
```json
{{
    "criterion": "{criterion}",
    "score": 1-5,
    "passed": true/false,
    "notes": "Brief explanation of what you observed in the image and why you gave this score",
    "confidence_percentage": 0-100,
    "visual_markers": ["marker1", "marker2"],
    "comparison_notes": "How it compares to authentic versions"
}}
```

# Requirements:
- Focus on qualitative visual observations from the image
- Look for actual defects: wrong colors, poor stitching, blurry logos, cheap materials, incorrect patterns
- Consider if features match what's expected (colors, patterns, materials, textures)
- Give objective scores based on what you can actually see in THIS specific image for THIS specific criterion
- Provide specific visual evidence for your score
- Be thorough and fair in your assessment
- Remember: you're only evaluating ONE criterion from ONE image
"""
