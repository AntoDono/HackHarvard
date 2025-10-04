"""
Brand Detection Module

Automatically identifies brands from Google Lens results and maps them to official websites.
"""

from typing import Dict, Optional
from .config import KNOWN_BRANDS


class BrandDetector:
    """Detects brands from search results and identifies official websites."""
    
    def __init__(self):
        """Initialize brand detector with known brand mappings."""
        self.known_brands = KNOWN_BRANDS
    
    def identify_from_lens_results(self, lens_data: Dict) -> Optional[Dict]:
        """
        Identify the brand from Google Lens results.
        
        Args:
            lens_data: Raw Google Lens API response
            
        Returns:
            Dict with brand info: {'name': str, 'official_website': str, 'confidence': float}
            or None if no brand detected
        """
        brand_candidates = []
        
        # Check different result sections with priority
        sections = [
            ('knowledge_graph', lens_data.get('knowledge_graph'), 1.0),
            ('exact_matches', lens_data.get('exact_matches', [])[:5], 0.95),
            ('visual_matches', lens_data.get('visual_matches', [])[:10], 0.7)
        ]
        
        for section_name, section_data, base_confidence in sections:
            if not section_data:
                continue
                
            # Handle knowledge graph (dict) vs matches (list)
            items = [section_data] if isinstance(section_data, dict) else section_data
            
            for item in items:
                text = f"{item.get('title', '')} {item.get('source', '')}".lower()
                
                for brand, website in self.known_brands.items():
                    if brand in text:
                        brand_candidates.append({
                            'name': brand.title(),
                            'official_website': website,
                            'source': section_name,
                            'confidence': base_confidence
                        })
        
        # Return highest confidence brand
        if brand_candidates:
            return max(brand_candidates, key=lambda x: (x['confidence'], -len(x['source'])))
        
        return None
    
    def get_official_website(self, brand_name: str) -> Optional[str]:
        """
        Get official website for a brand name.
        
        Args:
            brand_name: Brand name to look up
            
        Returns:
            Official website domain or None
        """
        brand_lower = brand_name.lower()
        return self.known_brands.get(brand_lower)
    
    def is_known_brand(self, brand_name: str) -> bool:
        """Check if brand is in the known brands database."""
        return brand_name.lower() in self.known_brands
    
    def get_all_brands(self) -> Dict[str, str]:
        """Get all known brand mappings."""
        return self.known_brands.copy()

