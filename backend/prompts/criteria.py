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
For a {item}, provide exactly 5 specific authentication criteria. For each criterion, specify:
1. WHAT authentic features should look like - BE VERY SPECIFIC about colors, patterns, textures, finishes
2. WHERE/HOW to photograph it

CRITICAL REQUIREMENTS:
- Include SPECIFIC COLORS (e.g., "navy blue", "gold metallic", "brown leather")
- Include SPECIFIC PATTERNS (e.g., "checkered", "monogram", "textured")
- Include SPECIFIC MATERIALS (e.g., "canvas", "leather", "metal")
- Include SPECIFIC FINISHES (e.g., "matte", "glossy", "brushed")
- Be concrete and visual, not abstract

# Format
Format your response as a JSON object with two arrays that map 1-to-1:
```json
{{
  "criteria": [
    "Brown vachetta leather trim with natural tan color that darkens to honey patina",
    "Beige and brown monogram canvas with LV logo pattern",
    "Gold brass hardware with brushed finish",
    "Red interior lining in cross-grain leather",
    "Date code stamped in black ink on leather tab"
  ],
  "location_angle": [
    "Leather trim on handles, close-up in natural light",
    "Front center showing full monogram pattern",
    "Zipper pull and clasp, angled view",
    "Interior pocket area, top-down view",
    "Inside pocket, leather tab close-up"
  ]
}}
```

# Examples:

**Good criterion** (specific): "Baby blue grained calfskin leather with soft pebbled texture"
**Bad criterion** (generic): "Fine-grained, supple leather trim" ❌

**Good criterion** (specific): "White LV monogram print on baby blue background with precise spacing"
**Bad criterion** (generic): "Sharp, well-defined logo with perfect spacing" ❌

**Good criterion** (specific): "Gold-toned metal snap button with engraved LV logo"
**Bad criterion** (generic): "Polished metal hardware with engraved logo" ❌

**Good criterion** (specific): "Pink fabric interior lining with cross-hatch texture"
**Bad criterion** (generic): "Quality interior lining material" ❌

# Requirements:
- ALWAYS mention specific colors and materials
- ALWAYS describe the actual appearance, not just quality
- Use concrete visual descriptors that CLIP can understand
- Each location_angle should describe WHERE/HOW to photograph it
- Include specific views: "front", "back", "interior", "close-up", "when opened", "side view", "macro shot"
- Must have the most up to date information, use the internet to get the most recent information about this specific item
- Research the EXACT item and its authentic characteristics

Return your response in the proper format.
"""
