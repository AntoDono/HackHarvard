"""
Image Search Module

Main module for reverse image search using Google Lens API with counterfeit detection.
"""

import requests
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

from .brand_detector import BrandDetector
from .trust_scorer import TrustScorer
from .utils import calculate_similarity_score

load_dotenv()


class ReverseImageSearcher:
    """
    Reverse image search for counterfeit detection.
    
    Uses Google Lens API to find similar images, automatically identifies brands,
    applies trust scoring, and provides authentication verdicts.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the reverse image searcher."""
        self.api_key = api_key or os.getenv('SERPAPI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "SerpApi API key is required. Set SERPAPI_API_KEY environment "
                "variable or pass api_key parameter."
            )
        
        self.brand_detector = BrandDetector()
        self.trust_scorer = TrustScorer()
    
    def search_by_image_url(self, image_url: str, max_results: int = 10) -> List[Dict]:
        """
        Search for similar images using Google Lens API.
        Automatically identifies brand and locates official website.
        
        Args:
            image_url: URL of the image to search
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with trust scores and brand info
        """
        try:
            # Make Google Lens API request
            params = {
                'engine': 'google_lens',
                'url': image_url,
                'api_key': self.api_key,
                'hl': 'en',
            }
            
            print(f"🔍 Searching with Google Lens API: {image_url}")
            
            response = requests.get("https://serpapi.com/search", params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if 'error' in data:
                print(f"❌ SerpApi Error: {data['error']}")
                return []
            
            print(f"📊 Available sections: {list(data.keys())}")
            
            # Identify brand from results
            detected_brand = self.brand_detector.identify_from_lens_results(data)
            if detected_brand:
                print(f"🏷️  Detected brand: {detected_brand['name']}")
                print(f"🌐 Official website: {detected_brand['official_website']}")
                self._add_brand_to_trust_scores(detected_brand)
            
            # Extract results
            image_results = []
            
            # Process exact matches
            if 'exact_matches' in data and data['exact_matches']:
                print(f"✅ Found {len(data['exact_matches'])} exact matches")
                for i, result in enumerate(data['exact_matches'][:max_results]):
                    image_results.append(self._process_result(result, image_url, 'Exact Matches', True))
            
            # Process visual matches
            if 'visual_matches' in data and data['visual_matches']:
                print(f"🎯 Found {len(data['visual_matches'])} visual matches")
                remaining = max_results - len(image_results)
                for result in data['visual_matches'][:remaining]:
                    image_results.append(self._process_result(result, image_url, 'Visual Matches', False))
            
            print(f"📦 Total results collected: {len(image_results)}")
            
            if not image_results:
                print("⚠️  No results found in any section")
                return []
            
            # Limit to requested number
            image_results = image_results[:max_results]
            
            # Apply frequency-based trust boost
            image_results = self.trust_scorer.apply_frequency_boost(image_results)
            
            # Add detected brand info to results
            if image_results and detected_brand:
                for result in image_results:
                    result['detected_brand'] = detected_brand['name']
                    result['official_website'] = detected_brand['official_website']
            
            print(f"✅ Returning {len(image_results)} results from Google Lens")
            return image_results
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {e}")
            return []
        except Exception as e:
            print(f"❌ Error searching with Google Lens: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def search_by_local_image(self, image_path: str, max_results: int = 10) -> List[Dict]:
        """Search for similar images using a local image file."""
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            import base64
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            # Use SerpApi with base64 encoded image
            params = {
                'engine': 'google_lens',
                'image': image_b64,
                'api_key': self.api_key,
                'hl': 'en',
            }
            
            print(f"🔍 Searching with local image: {image_path}")
            
            response = requests.post("https://serpapi.com/search", data=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            # Process similar to search_by_image_url
            # (Implementation similar to above, using the data response)
            return self.search_by_image_url(image_path, max_results)
            
        except Exception as e:
            print(f"Error searching with local image: {e}")
            return []
    
    def _process_result(self, result: Dict, original_url: str, section: str, is_exact: bool) -> Dict:
        """Process a single search result."""
        similarity_score = calculate_similarity_score(result, original_url)
        
        price_info = result.get('price', {})
        price_str = price_info.get('value', '') if isinstance(price_info, dict) else ''
        
        return {
            'position': 0,  # Will be set later
            'title': result.get('title', ''),
            'link': result.get('link', ''),
            'displayed_link': result.get('source', ''),
            'thumbnail': result.get('thumbnail', '') or result.get('image', ''),
            'snippet': result.get('title', ''),
            'source': result.get('source', ''),
            'trust_score': self.trust_scorer.get_domain_trust_score(result.get('link', '')),
            'similarity_score': similarity_score,
            'image_resolution': f"{result.get('image_width', '')}x{result.get('image_height', '')}" if result.get('image_width') else '',
            'date': '',
            'section': section,
            'is_exact_match': is_exact,
            'price': price_str,
            'rating': result.get('rating'),
            'reviews': result.get('reviews')
        }
    
    def _add_brand_to_trust_scores(self, brand_info: Dict):
        """Add detected brand's official website to trust scores."""
        if not brand_info or not brand_info.get('official_website'):
            return
        
        try:
            from urllib.parse import urlparse
            domain = urlparse(f"https://{brand_info['official_website']}").netloc.replace('www.', '')
            self.trust_scorer.add_trusted_domain(domain, 1.0)
        except:
            pass
    
    def filter_by_trust_score(self, results: List[Dict], min_trust: float = 0.5) -> List[Dict]:
        """Filter results by minimum trust score."""
        return [r for r in results if r.get('trust_score', 0) >= min_trust]
    
    def get_high_trust_results(self, results: List[Dict]) -> List[Dict]:
        """Get only high-trust results (≥0.8)."""
        return self.filter_by_trust_score(results, min_trust=0.8)
    
    def get_official_results(self, results: List[Dict]) -> List[Dict]:
        """Get results from official brand website."""
        official_results = []
        for result in results:
            if result.get('official_website'):
                if result['official_website'] in result.get('link', ''):
                    official_results.append(result)
        return official_results

