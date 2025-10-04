def get_criteria_prompt(item: str) -> str:
    """
    Generate the prompt for authentication criteria with detailed location info and backups.
    
    Args:
        item: The name/type of item to check
        
    Returns:
        str: The formatted prompt
    """
    return f"""
    
# Goal    
You are an expert in authenticating luxury goods and identifying counterfeits.

# Task
For a {item}, provide exactly 5 specific authentication criteria. For EACH criterion, you MUST provide:

1. **Primary Feature**: What to look for with EXTREME detail (colors, patterns, textures, finishes)
2. **Location & Why**: Exact location on the item AND why this spot matters for authentication
3. **How to Photograph**: Specific instructions (angle, distance, lighting)
4. **Backup Feature**: Alternative feature to check if primary location is not accessible/visible
5. **Backup Location**: Where to find the backup feature and how to photograph it

CRITICAL REQUIREMENTS:
- Include SPECIFIC COLORS (e.g., "navy blue", "gold metallic", "brown leather")
- Include SPECIFIC PATTERNS (e.g., "checkered", "monogram", "textured")
- Include SPECIFIC MATERIALS (e.g., "canvas", "leather", "metal")
- Include SPECIFIC FINISHES (e.g., "matte", "glossy", "brushed")
- Explain WHY each location is important (e.g., "this area is hard for counterfeiters to replicate")
- Be concrete and visual, not abstract

# Format
Format your response as a JSON object:
```json
{{
  "criteria": [
    {{
      "primary_feature": "Brown vachetta leather trim with natural tan color that darkens to honey patina, untreated and oxidizes over time",
      "primary_location": "Top handles and side straps",
      "why_important": "Authentic vachetta leather oxidizes naturally from light tan to rich honey brown - counterfeit leather often uses dye or coating that doesn't age naturally",
      "how_to_photograph": "Close-up shot (6-12 inches away) of handle in natural daylight, showing the gradient of color if aged, or the pale tan if new",
      "backup_feature": "Leather pull tabs on zipper with same vachetta leather characteristics",
      "backup_location": "Main zipper at top of bag",
      "backup_how_to_photograph": "Macro shot of zipper pull tab showing leather grain and color, natural lighting from side angle"
    }},
    {{
      "primary_feature": "Beige and brown monogram canvas with LV logo pattern, letters should be symmetrical and evenly spaced with brown 'LV' on beige background",
      "primary_location": "Front center panel of bag",
      "why_important": "The monogram pattern should align perfectly at seams - authentic bags are cut from a single piece of canvas with pattern alignment, counterfeits often have misaligned patterns",
      "how_to_photograph": "Straight-on front view, 12-18 inches away, showing full monogram pattern and how it aligns at edges/seams",
      "backup_feature": "Monogram pattern on the back panel, checking for same alignment and symmetry",
      "backup_location": "Rear panel of bag",
      "backup_how_to_photograph": "Straight-on rear view at same distance, showing pattern continuity and seam alignment"
    }}
  ]
}}
```

# Examples:

**Good detailed criterion**:
- Primary Feature: "Baby blue grained calfskin leather with soft pebbled texture, approximately 2-3mm grain size, matte finish"
- Location & Why: "Entire exterior surface - this specific leather type and grain size is proprietary to the brand's tannery"
- How to Photograph: "Multiple angles in natural light: front straight-on, side at 45°, close-up macro of grain texture"

**Bad generic criterion** ❌:
- "Fine-grained, supple leather trim"
- "On the bag"
- "Take a photo"

# Requirements:
- ALWAYS explain WHERE and WHY for each location
- ALWAYS provide a backup option in case primary feature isn't accessible
- ALWAYS mention specific colors and materials
- ALWAYS describe the actual appearance, not just quality
- Each backup should be realistic and achievable (don't suggest impossible angles)
- Must have the most up to date information, use the internet to get the most recent information about this specific item
- Research the EXACT item and its authentic characteristics
- Backup features should be equally distinctive and verifiable

Return ONLY valid JSON in the exact format shown above.
"""
