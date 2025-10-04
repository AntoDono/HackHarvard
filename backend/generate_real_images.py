#!/usr/bin/env python3
"""
Reverse Image Search for Counterfeit Detection

This module provides functionality to search for similar images using SerpApi's
Google Reverse Image Search API, with focus on finding authentic reference images
for counterfeit detection purposes.

Features:
- Reverse image search using image URLs, local files, or PIL Image objects
- Trust scoring system for different domains (brand sites, resale platforms, etc.)
- High-quality image extraction from source pages
- Similarity scoring for exact product matching
- Filtering and ranking capabilities for counterfeit detection
"""

import requests
import json
import os
import re
from typing import List, Dict, Optional
from PIL import Image
import io
import base64
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Load environment variables
load_dotenv()


class ReverseImageSearcher:
    """
    A class for performing reverse image searches with focus on counterfeit detection.
    
    This class uses SerpApi's Google Reverse Image Search to find similar images,
    then applies trust scoring and similarity analysis to identify authentic
    reference images for counterfeit detection.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the reverse image searcher with SerpApi key."""
        self.api_key = api_key or os.getenv('SERPAPI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "SerpApi API key is required. Set SERPAPI_API_KEY environment "
                "variable or pass api_key parameter."
            )
        
        # Trust scores for different domains (higher = more trustworthy)
        self.trust_scores = self._initialize_trust_scores()
    
    def _initialize_trust_scores(self) -> Dict[str, float]:
        """Initialize the trust scoring system for different domains."""
        return {
            # Official brand websites (highest trust)
            'nike.com': 1.0,
            'adidas.com': 1.0,
            'louisvuitton.com': 1.0,
            'gucci.com': 1.0,
            'chanel.com': 1.0,
            'hermes.com': 1.0,
            'rolex.com': 1.0,
            'omega.com': 1.0,
            'patek.com': 1.0,
            'how2work.com': 1.0,  # Labubu official
            'popmart.com': 1.0,   # Pop Mart official
            
            # Verified resale platforms (high trust)
            'stockx.com': 0.9,
            'grailed.com': 0.9,
            'therealreal.com': 0.9,
            'vestiairecollective.com': 0.9,
            'goat.com': 0.9,
            'stadiumgoods.com': 0.9,
            
            # General retailers (medium trust)
            'amazon.com': 0.6,
            'ebay.com': 0.5,
            'etsy.com': 0.4,
            
            # Social media and blogs (low trust)
            'instagram.com': 0.3,
            'pinterest.com': 0.3,
            'reddit.com': 0.2,
        }
    
    def get_domain_trust_score(self, url: str) -> float:
        """
        Get trust score for a domain using both hardcoded scores and dynamic verification.
        
        Uses multiple signals:
        1. Hardcoded trust scores for known brands
        2. HTTPS vs HTTP
        3. Domain age/reputation indicators (via domain patterns)
        4. Official brand indicators in domain name
        5. Verified retailer patterns
        
        Returns:
            float: Trust score between 0 and 1
        """
        if not url:
            return 0.0
        
        try:
            # Extract domain and path from URL
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Check hardcoded trust scores first (known brands)
            if domain in self.trust_scores:
                return self.trust_scores[domain]
            
            # Dynamic trust scoring for unknown domains
            score = 0.3  # Base score for unknown domains
            
            # Factor 1: HTTPS increases trust
            if parsed.scheme == 'https':
                score += 0.1
            
            # Factor 2: Official brand indicators in domain
            official_indicators = [
                'official', 'store', 'shop', 'retail', 'direct',
                'authentic', 'authorized', 'certified'
            ]
            if any(indicator in domain for indicator in official_indicators):
                score += 0.15
            
            # Factor 3: Known e-commerce platforms (medium trust)
            trusted_platforms = [
                'shopify.com', 'bigcommerce.com', 'wix.com', 'squarespace.com',
                'myshopify.com', 'ebay.', 'amazon.', 'walmart.', 'target.com'
            ]
            if any(platform in domain for platform in trusted_platforms):
                score = max(score, 0.5)  # At least medium trust
            
            # Factor 4: Red flags (reduce trust)
            red_flags = [
                'replica', 'fake', 'knock-off', 'knockoff', 'copy',
                'cheap', 'discount', 'wholesale', 'bulk'
            ]
            if any(flag in domain or flag in path for flag in red_flags):
                score -= 0.3
            
            # Factor 5: Country code TLDs (some are more trustworthy)
            high_trust_tlds = ['.com', '.org', '.net', '.gov', '.edu']
            if any(domain.endswith(tld) for tld in high_trust_tlds):
                score += 0.05
            
            # Factor 6: Short, clean domains are more trustworthy
            domain_parts = domain.split('.')
            if len(domain_parts) == 2 and len(domain_parts[0]) < 20:
                score += 0.05
            
            # Clamp score between 0 and 1
            return min(1.0, max(0.0, score))
        
        except Exception as e:
            print(f"Error calculating trust score for {url}: {e}")
            return 0.3  # Default to low-medium trust
    
    def extract_high_quality_images(self, page_url: str, max_images: int = 5) -> List[str]:
        """
        Extract high-quality images from a webpage.
        
        Args:
            page_url: URL of the webpage to extract images from
            max_images: Maximum number of images to extract
            
        Returns:
            List of high-quality image URLs
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                             '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(page_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            image_urls = []
            
            # Find all img tags
            img_tags = soup.find_all('img')
            
            for img in img_tags:
                # Try different attributes for image URLs
                img_url = None
                for attr in ['data-src', 'data-original', 'data-lazy', 'src']:
                    if img.get(attr):
                        img_url = img.get(attr)
                        break
                
                if not img_url:
                    continue
                
                # Convert relative URLs to absolute
                img_url = self._normalize_image_url(img_url, page_url)
                
                # Filter for high-quality images
                if self.is_high_quality_image(img_url):
                    image_urls.append(img_url)
                    
                    if len(image_urls) >= max_images:
                        break
            
            return image_urls
            
        except Exception as e:
            print(f"Error extracting images from {page_url}: {e}")
            return []
    
    def _normalize_image_url(self, img_url: str, base_url: str) -> str:
        """Convert relative URLs to absolute URLs."""
        if img_url.startswith('//'):
            return 'https:' + img_url
        elif img_url.startswith('/'):
            return urljoin(base_url, img_url)
        elif not img_url.startswith('http'):
            return urljoin(base_url, img_url)
        return img_url
    
    def is_high_quality_image(self, img_url: str) -> bool:
        """
        Check if an image URL is likely to be high quality.
        
        Args:
            img_url: URL of the image to check
            
        Returns:
            True if the image is likely high quality, False otherwise
        """
        try:
            # Skip very small images
            if any(size in img_url.lower() for size in ['thumb', 'small', 'mini', 'icon']):
                return False
            
            # Look for high-res indicators
            high_res_indicators = [
                'large', 'big', 'high', 'hd', 'full', 'original', 
                'max', 'zoom', 'detail', 'product', 'main'
            ]
            
            if any(indicator in img_url.lower() for indicator in high_res_indicators):
                return True
            
            # Check for common high-res patterns
            if re.search(r'[0-9]{3,4}x[0-9]{3,4}', img_url):
                return True
            
            # Check for common image extensions
            if any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                return True
            
            return False
            
        except:
            return False
    
    def search_by_image_url(self, image_url: str, max_results: int = 10) -> List[Dict]:
        """
        Search for similar images using Google Lens API.
        Returns visual matches, exact matches, and product information.
        Automatically identifies brand and locates official website.
        """
        try:
            # SerpApi Google Lens endpoint
            url = "https://serpapi.com/search"
            
            params = {
                'engine': 'google_lens',
                'url': image_url,  # Note: 'url' parameter for Google Lens, not 'image_url'
                'api_key': self.api_key,
                'hl': 'en',  # Language
            }
            
            print(f"🔍 Searching with Google Lens API: {image_url}")
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for errors
            if 'error' in data:
                print(f"❌ SerpApi Error: {data['error']}")
                return []
            
            # Debug: Show what sections are available
            print(f"📊 Available sections: {list(data.keys())}")
            
            # Identify brand from results
            detected_brand = self._identify_brand_from_results(data)
            if detected_brand:
                print(f"🏷️  Detected brand: {detected_brand['name']}")
                if detected_brand.get('official_website'):
                    print(f"🌐 Official website: {detected_brand['official_website']}")
                    # Update trust scores dynamically with the detected brand
                    self._add_brand_to_trust_scores(detected_brand)
            
            # Extract and process results from multiple sections
            image_results = []
            
            # Priority 1: Exact matches (best for counterfeit detection)
            if 'exact_matches' in data and data['exact_matches']:
                print(f"✅ Found {len(data['exact_matches'])} exact matches")
                for i, result in enumerate(data['exact_matches'][:max_results]):
                    similarity_score = self.calculate_similarity_score(result, image_url)
                    
                    image_info = {
                        'position': len(image_results) + 1,
                        'title': result.get('title', ''),
                        'link': result.get('link', ''),
                        'displayed_link': result.get('source', ''),
                        'thumbnail': result.get('thumbnail', ''),
                        'snippet': result.get('title', ''),  # Lens doesn't always have snippets
                        'source': result.get('source', ''),
                        'trust_score': self.get_domain_trust_score(result.get('link', '')),
                        'similarity_score': similarity_score,
                        'image_resolution': f"{result.get('image_width', '')}x{result.get('image_height', '')}" if result.get('image_width') else '',
                        'date': '',
                        'section': 'Exact Matches',
                        'is_exact_match': True
                    }
                    image_results.append(image_info)
            
            # Priority 2: Visual matches (visually similar products)
            if 'visual_matches' in data and data['visual_matches']:
                print(f"🎯 Found {len(data['visual_matches'])} visual matches")
                for i, result in enumerate(data['visual_matches'][:max_results]):
                    similarity_score = self.calculate_similarity_score(result, image_url)
                    
                    # Extract price information if available
                    price_info = result.get('price', {})
                    price_str = price_info.get('value', '') if isinstance(price_info, dict) else ''
                    
                    image_info = {
                        'position': len(image_results) + 1,
                        'title': result.get('title', ''),
                        'link': result.get('link', ''),
                        'displayed_link': result.get('source', ''),
                        'thumbnail': result.get('thumbnail', ''),
                        'snippet': result.get('title', ''),
                        'source': result.get('source', ''),
                        'trust_score': self.get_domain_trust_score(result.get('link', '')),
                        'similarity_score': similarity_score,
                        'image_resolution': f"{result.get('image_width', '')}x{result.get('image_height', '')}" if result.get('image_width') else '',
                        'date': '',
                        'section': 'Visual Matches',
                        'is_exact_match': False,
                        'price': price_str,
                        'rating': result.get('rating'),
                        'reviews': result.get('reviews')
                    }
                    image_results.append(image_info)
            
            print(f"📦 Total results collected: {len(image_results)}")
            
            if not image_results:
                print("⚠️  No results found in any section")
                print(f"Available sections: {list(data.keys())}")
                return []
            
            # Limit to requested number
            image_results = image_results[:max_results]
            
            # Apply frequency-based trust boost
            image_results = self._apply_frequency_trust_boost(image_results)
            
            # Add detected brand info to results metadata
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
    
    def _get_known_brands(self) -> Dict[str, str]:
        """Return mapping of brand keywords to official websites."""
        return {
            # Sneakers & Athletic
            'nike': 'nike.com', 'jordan': 'nike.com', 'air jordan': 'nike.com',
            'adidas': 'adidas.com', 'yeezy': 'adidas.com/yeezy',
            'new balance': 'newbalance.com', 'converse': 'converse.com',
            'vans': 'vans.com', 'puma': 'puma.com', 'reebok': 'reebok.com',
            'asics': 'asics.com', 'under armour': 'underarmour.com',
            
            # Luxury Fashion
            'louis vuitton': 'louisvuitton.com', 'lv': 'louisvuitton.com',
            'gucci': 'gucci.com', 'chanel': 'chanel.com',
            'prada': 'prada.com', 'hermes': 'hermes.com', 'hermès': 'hermes.com',
            'balenciaga': 'balenciaga.com', 'burberry': 'burberry.com',
            'versace': 'versace.com', 'fendi': 'fendi.com', 'dior': 'dior.com',
            'saint laurent': 'ysl.com', 'ysl': 'ysl.com',
            'bottega veneta': 'bottegaveneta.com', 'givenchy': 'givenchy.com',
            'alexander mcqueen': 'alexandermcqueen.com',
            
            # Watches
            'rolex': 'rolex.com', 'omega': 'omegawatches.com',
            'cartier': 'cartier.com',
            
            # Streetwear
            'supreme': 'supremenewyork.com', 'off-white': 'off---white.com',
            
            # Collectibles
            'labubu': 'how2work.com', 'pop mart': 'popmart.com',
            
            # Outdoor
            'the north face': 'thenorthface.com', 'patagonia': 'patagonia.com',
        }
    
    def _identify_brand_from_results(self, lens_data: Dict) -> Dict:
        """
        Identify the brand from Google Lens results.
        
        Args:
            lens_data: Raw Google Lens API response
            
        Returns:
            Dict with brand info: {'name': str, 'official_website': str, 'confidence': float}
        """
        brand_candidates = []
        known_brands = self._get_known_brands()
        
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
                
                for brand, website in known_brands.items():
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
    
    def _add_brand_to_trust_scores(self, brand_info: Dict):
        """Dynamically add detected brand to trust scores."""
        if not brand_info or not brand_info.get('official_website'):
            return
        
        try:
            from urllib.parse import urlparse
            domain = urlparse(f"https://{brand_info['official_website']}").netloc.replace('www.', '')
            
            if domain and domain not in self.trust_scores:
                self.trust_scores[domain] = 1.0
                print(f"✅ Added {domain} to trusted sources (score: 1.0)")
        except:
            pass
    
    def _apply_frequency_trust_boost(self, results: List[Dict]) -> List[Dict]:
        """Apply trust boost based on domain frequency (more appearances = more trustworthy)."""
        if not results:
            return results
        
        from collections import Counter
        from urllib.parse import urlparse
        
        # Count domain appearances
        domain_counts = Counter()
        for result in results:
            if url := result.get('link'):
                try:
                    domain = urlparse(url).netloc.lower().replace('www.', '')
                    domain_counts[domain] += 1
                except:
                    pass
        
        # Apply frequency boost
        for result in results:
            if url := result.get('link'):
                try:
                    domain = urlparse(url).netloc.lower().replace('www.', '')
                    count = domain_counts.get(domain, 1)
                    
                    # Determine boost: 3+ times = 0.15, 2 times = 0.08, 1 time = 0
                    boost = 0.15 if count >= 3 else (0.08 if count == 2 else 0.0)
                    
                    result['trust_score'] = min(1.0, result.get('trust_score', 0) + boost)
                    result['frequency_boost'] = boost
                    result['domain_frequency'] = count
                except:
                    pass
        
        return results
    
    def calculate_similarity_score(self, result: Dict, original_url: str) -> float:
        """Calculate similarity score based on title, snippet, and image quality."""
        try:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
            score = 0.5  # Base score
            
            # Positive indicators
            exact_keywords = ['product', 'item', 'model', 'sku', 'authentic', 'genuine', 'official']
            score += 0.1 * sum(1 for kw in exact_keywords if kw in text)
            
            # Negative indicators
            generic_keywords = ['similar', 'like', 'related', 'compare', 'alternative']
            score -= 0.1 * sum(1 for kw in generic_keywords if kw in text)
            
            # Brand consistency bonus
            brands = ['nike', 'adidas', 'louis vuitton']
            for brand in brands:
                if brand in original_url.lower() and brand in text:
                    score += 0.2
                    break
            
            # High resolution bonus
            if res := result.get('image_resolution', ''):
                try:
                    if 'x' in res:
                        w, h = map(int, res.split('x'))
                        if w > 400 and h > 400:
                            score += 0.1
                except:
                    pass
            
            return max(0.0, min(1.0, score))
        except:
            return 0.5
    
    def search_by_local_image(self, image_path: str, max_results: int = 10) -> List[Dict]:
        """Search for similar images using a local image file."""
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            img_base64 = base64.b64encode(image_data).decode()
            image_url = f"data:image/jpeg;base64,{img_base64}"
            
            return self.search_by_image_url(image_url, max_results)
            
        except FileNotFoundError:
            print(f"Image file not found: {image_path}") 
            return []
        except Exception as e:
            print(f"Error processing local image: {e}")
            return []
    
    def search_by_pil_image(self, image: Image.Image, max_results: int = 10) -> List[Dict]:
        """Search for similar images using a PIL Image object."""
        try:
            buffered = io.BytesIO()
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(buffered, format="JPEG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            image_url = f"data:image/jpeg;base64,{img_base64}"
            
            return self.search_by_image_url(image_url, max_results)
            
        except Exception as e:
            print(f"Error processing PIL image: {e}")
            return []
    
    def filter_by_trust_score(self, results: List[Dict], min_trust: float = 0.5) -> List[Dict]:
        """Filter results by minimum trust score."""
        return [result for result in results if result['trust_score'] >= min_trust]
    
    def get_high_trust_results(self, results: List[Dict]) -> List[Dict]:
        """Get only high-trust results (trust score >= 0.8)."""
        return self.filter_by_trust_score(results, min_trust=0.8)
    
    def get_top_3_image_links(self, results: List[Dict], use_high_quality: bool = True, 
                            min_similarity: float = 0.3) -> List[Dict]:
        """
        Get direct links to the top 3 most confident images with similarity filtering.
        
        Args:
            results: List of search results
            use_high_quality: Whether to extract high-quality images from source pages
            min_similarity: Minimum similarity score threshold
            
        Returns:
            List of top 3 image information dictionaries
        """
        if not results:
            return []
        
        # Filter by minimum similarity score first
        filtered_results = [r for r in results if r.get('similarity_score', 0) >= min_similarity]
        
        if not filtered_results:
            print(f"⚠️  No results meet minimum similarity threshold ({min_similarity})")
            # Fallback to original results if no good matches
            filtered_results = results
        
        # Sort by combined score (trust + similarity) and take top 3
        top_3 = sorted(
            filtered_results, 
            key=lambda x: (x['trust_score'] * 0.6 + x.get('similarity_score', 0) * 0.4), 
            reverse=True
        )[:3]
        
        image_links = []
        for i, result in enumerate(top_3, 1):
            # Try to get high-quality images from source page
            high_quality_images = []
            if use_high_quality and result.get('link'):
                print(f"🔍 Extracting high-quality images from: {result['link']}")
                high_quality_images = self.extract_high_quality_images(result['link'], max_images=3)
            
            # Use the best available image
            best_image_url = result.get('thumbnail', '')
            if high_quality_images:
                best_image_url = high_quality_images[0]  # Use the first (best) high-quality image
                print(f"✅ Found {len(high_quality_images)} high-quality images")
            else:
                print(f"⚠️  Using SerpApi thumbnail (lower quality)")
            
            # Calculate combined score
            combined_score = result['trust_score'] * 0.6 + result.get('similarity_score', 0) * 0.4
            
            image_info = {
                'rank': i,
                'confidence': result['trust_score'],
                'similarity': result.get('similarity_score', 0),
                'combined_score': combined_score,
                'confidence_level': 'HIGH' if result['trust_score'] >= 0.8 else 'MEDIUM' if result['trust_score'] >= 0.5 else 'LOW',
                'similarity_level': 'HIGH' if result.get('similarity_score', 0) >= 0.7 else 'MEDIUM' if result.get('similarity_score', 0) >= 0.4 else 'LOW',
                'title': result['title'],
                'source': result['source'],
                'domain': result['displayed_link'],
                'page_link': result['link'],
                'image_url': best_image_url,
                'high_quality_images': high_quality_images,
                'description': result.get('snippet', ''),
                'resolution': result.get('image_resolution', ''),
                'is_high_quality': len(high_quality_images) > 0
            }
            image_links.append(image_info)
        
        return image_links
    
    def print_top_3_with_links(self, results: List[Dict], use_high_quality: bool = True):
        """Print top 3 results with direct image links."""
        top_3 = self.get_top_3_image_links(results, use_high_quality)
        
        if not top_3:
            print("No results found.")
            return
        
        print(f"\n🏆 TOP 3 MOST CONFIDENT IMAGES:")
        print("="*80)
        
        for result in top_3:
            trust_indicator = "✓" if result['confidence'] >= 0.8 else "⚠" if result['confidence'] >= 0.5 else "✗"
            similarity_indicator = "🎯" if result.get('similarity', 0) >= 0.7 else "🔍" if result.get('similarity', 0) >= 0.4 else "❓"
            quality_indicator = "🔥" if result.get('is_high_quality', False) else "📷"
            
            print(f"\n{result['rank']}. {trust_indicator} CONFIDENCE: {result['confidence_level']} ({result['confidence']:.2f})")
            print(f"   {similarity_indicator} SIMILARITY: {result.get('similarity_level', 'UNKNOWN')} ({result.get('similarity', 0):.2f})")
            print(f"   📊 COMBINED SCORE: {result.get('combined_score', 0):.2f}")
            print(f"   📝 Title: {result['title']}")
            print(f"   🌐 Source: {result['source']}")
            print(f"   🔗 Domain: {result['domain']}")
            print(f"   🔗 Page Link: {result['page_link']}")
            
            if result['image_url']:
                print(f"   {quality_indicator} Image Link: {result['image_url']}")
                if result.get('is_high_quality'):
                    print(f"   ✅ High-quality image extracted from source page")
                else:
                    print(f"   ⚠️  Using SerpApi thumbnail (lower quality)")
            else:
                print(f"   🖼️  Image Link: Not available")
            
            # Show additional high-quality images if available
            if result.get('high_quality_images') and len(result['high_quality_images']) > 1:
                print(f"   🔥 Additional high-quality images found:")
                for i, img_url in enumerate(result['high_quality_images'][1:], 2):
                    print(f"      {i}. {img_url}")
            
            if result['description']:
                print(f"   📄 Description: {result['description'][:120]}...")
            if result['resolution']:
                print(f"   📐 Resolution: {result['resolution']}")
            print("-" * 80)
    
    def print_results(self, results: List[Dict], show_all: bool = True):
        """Print search results in a formatted way."""
        if not results:
            print("No results found.")
            return
        
        print(f"\nFound {len(results)} results:")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            trust_indicator = "✓" if result['trust_score'] >= 0.8 else "⚠" if result['trust_score'] >= 0.5 else "✗"
            
            print(f"\n{i}. {trust_indicator} Trust: {result['trust_score']:.2f}")
            print(f"   Title: {result['title']}")
            print(f"   Source: {result['source']}")
            print(f"   Link: {result['link']}")
            if result['snippet']:
                print(f"   Snippet: {result['snippet'][:100]}...")
            if result['image_resolution']:
                print(f"   Resolution: {result['image_resolution']}")
            
            if not show_all and i >= 5:  # Show only top 5 if not showing all
                print(f"\n... and {len(results) - 5} more results")
                break


def main():
    """Example usage of the ReverseImageSearcher with Google Lens API."""
    # Initialize searcher
    try:
        searcher = ReverseImageSearcher()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set your SerpApi API key:")
        print("export SERPAPI_API_KEY='your_api_key_here'")
        return
    
    # Example 1: Search using an image URL (Nike sneaker)
    print("=" * 80)
    print("🔍 GOOGLE LENS COUNTERFEIT DETECTION")
    print("=" * 80)
    
    image_url = "https://rqdnvzhjqdrmfwntcanq.supabase.co/storage/v1/object/public/image/labubu.png"
    print(f"\nSearching for: {image_url}")
    
    results = searcher.search_by_image_url(image_url, max_results=10)
    
    if results:
        print(f"\n✅ Found {len(results)} results from Google Lens")
        print("\n📊 Results by Section:")
        
        # Group by section
        exact_matches = [r for r in results if r.get('is_exact_match')]
        visual_matches = [r for r in results if not r.get('is_exact_match')]
        
        if exact_matches:
            print(f"\n🎯 EXACT MATCHES ({len(exact_matches)}):")
            for r in exact_matches[:3]:
                print(f"   • {r['title']}")
                print(f"     Source: {r['source']} (Trust: {r['trust_score']:.2f})")
                print(f"     Link: {r['link']}")
        
        if visual_matches:
            print(f"\n👀 VISUAL MATCHES ({len(visual_matches)}):")
            for r in visual_matches[:3]:
                price_info = f" - {r.get('price', 'N/A')}" if r.get('price') else ""
                print(f"   • {r['title']}{price_info}")
                print(f"     Source: {r['source']} (Trust: {r['trust_score']:.2f})")
                print(f"     Link: {r['link']}")
        
        # Show high-trust results
        high_trust = [r for r in results if r['trust_score'] >= 0.8]
        if high_trust:
            print(f"\n✅ HIGH-TRUST RESULTS ({len(high_trust)}):")
            for r in high_trust:
                print(f"   • {r['source']} - {r['title']}")
    else:
        print("\n❌ No results found")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()