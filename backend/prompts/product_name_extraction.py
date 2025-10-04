def get_product_name_extraction_prompt(product_name: str) -> str:
    """
    Generate the prompt for extracting clean product names.
    
    Args:
        product_name: Raw product name string (often from URLs or titles)
        
    Returns:
        str: The formatted prompt
    """
    return f"""Extract ONLY the core product name from this text. Remove:
- Platform names (eBay, Amazon, etc.)
- Edition markers (ENCORE EDITION, Limited Edition, etc.)
- Condition markers (NIP, BNIB, Used, New, etc.)
- Special characters like ~, |, -
- Extra descriptive text
- Seller information

Input: "{product_name}"

Return ONLY the clean product name, nothing else. Be concise.

Examples:
"NIP ~ McDonalds BTS Tiny Tan ~ RM ~ ENCORE EDITION | eBay" -> "McDonalds BTS Tiny Tan"
"Apple iPhone 15 Pro Max - 256GB - NEW - Factory Unlocked | Amazon" -> "Apple iPhone 15 Pro Max 256GB"
"Louis Vuitton Wallet | Authentic LV | eBay" -> "Louis Vuitton Wallet"

Now extract from the input above:"""
