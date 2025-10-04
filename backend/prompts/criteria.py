def get_criteria_prompt(item: str) -> str:
    """
    Generate the prompt for authentication criteria.
    
    Args:
        item: The name/type of item to check
        
    Returns:
        str: The formatted prompt
    """
    return f"""
    
# Goal    
You are an expert in authenticating luxury goods and identifying counterfeits.

# Task
For a {item}, provide exactly 5 specific criteria that authentication experts use to distinguish authentic items from counterfeits. 

# Format
Format your response as a json object:
```
[
    "First criterion",
    "Second criterion",
    "Third criterion",
    "Fourth criterion",
    "Fifth criterion"
]
```

# Requirement:
- Focus on visual inspections, physical details, markings, materials, craftsmanship, and other tangible features that can be verified through visual inspection.
- Must have the most up to date information, use the internet to get the most recent information.

"""

