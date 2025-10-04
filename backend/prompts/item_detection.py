def get_image_analysis_prompt(allow_repositioning: bool = True) -> str:
    """
    Generate the prompt for analyzing what's in an image.
    
    Args:
        allow_repositioning: Whether to allow repositioning suggestions
        
    Returns:
        str: The formatted prompt
    """
    if allow_repositioning:
        return """Analyze this image and identify what it contains. Return ONLY valid JSON.

Determine the PRIMARY content type:
- "person": If the image primarily shows a human/person
- "product": If the image primarily shows a product/item
- "text": If the image primarily shows text/document
- "other": For anything else (scenery, abstract, etc.)

Return format:
{
  "type": "person" | "product" | "text" | "other",
  "name": "Specific name/description of the main subject",
  "confidence": "High" | "Medium" | "Low",
  "description": "Brief description of what you see",
  "needs_repositioning": true/false,
  "repositioning_instructions": "Instructions if needed, otherwise null"
}

Examples:
- Person: {"type": "person", "name": "Person wearing Nike jacket", "confidence": "High", ...}
- Product: {"type": "product", "name": "Coca-Cola Classic 12oz can", "confidence": "High", ...}
- Text: {"type": "text", "name": "Business document", "confidence": "Medium", ...}

If unclear, set needs_repositioning: true with specific instructions."""
    else:
        return """Analyze this image and identify what it contains. Return ONLY valid JSON.

Determine the PRIMARY content type:
- "person": If the image primarily shows a human/person
- "product": If the image primarily shows a product/item
- "text": If the image primarily shows text/document
- "other": For anything else (scenery, abstract, etc.)

Return format:
{
  "type": "person" | "product" | "text" | "other",
  "name": "Specific name/description of the main subject",
  "confidence": "High" | "Medium" | "Low",
  "description": "Brief description of what you see"
}

Do your best to identify from the image provided."""


def get_price_search_prompt(product_name: str) -> str:
    """
    Generate the prompt for searching product price.
    
    Args:
        product_name: Full name of the product to search for
        
    Returns:
        str: The formatted prompt
    """
    return f"""Search the web for current pricing information for: {product_name}


Find the most recent pricing from reputable online retailers (Amazon, official brand stores, major retailers, etc.).
Convert all prices to USD if necessary.

Return ONLY valid JSON in this exact format:
```json
{{
  "min_price": <lowest price found as a number in USD>,
  "max_price": <highest price found as a number in USD>
}}
```

Example response:
```json
{{
  "min_price": 1199.0,
  "max_price": 1299.0
}}
```

Provide accurate, up-to-date USD pricing. Return only the JSON, no other text."""

