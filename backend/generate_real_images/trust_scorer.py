"""
Trust Scoring Module

Calculates trust scores for domains using hardcoded scores and dynamic analysis.
"""

from typing import Dict, List
from urllib.parse import urlparse
from collections import Counter

from .config import (
    TRUST_SCORES, TRUST_FACTORS, OFFICIAL_INDICATORS,
    TRUSTED_PLATFORMS, RED_FLAGS, HIGH_TRUST_TLDS,
    FREQUENCY_BOOST_HIGH, FREQUENCY_BOOST_MED,
    FREQUENCY_THRESHOLD_HIGH, FREQUENCY_THRESHOLD_MED
)


class TrustScorer:
    """Calculates and manages trust scores for domains."""
    
    def __init__(self):
        """Initialize trust scorer with base trust scores."""
        self.trust_scores = TRUST_SCORES.copy()
    
    def get_domain_trust_score(self, url: str) -> float:
        """
        Get trust score for a domain using hardcoded scores and dynamic verification.
        
        Uses multiple signals:
        1. Hardcoded trust scores for known brands
        2. HTTPS vs HTTP
        3. Official brand indicators in domain name
        4. Verified retailer patterns
        5. Red flags in domain/path
        
        Returns:
            Trust score between 0.0 and 1.0
        """
        if not url:
            return 0.0
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace('www.', '')
            path = parsed.path.lower()
            
            # Check hardcoded trust scores first
            if domain in self.trust_scores:
                return self.trust_scores[domain]
            
            # Dynamic trust scoring
            score = 0.3  # Base score
            
            # HTTPS bonus
            if parsed.scheme == 'https':
                score += TRUST_FACTORS['https_bonus']
            
            # Official keywords in domain
            if any(indicator in domain for indicator in OFFICIAL_INDICATORS):
                score += TRUST_FACTORS['official_keyword_bonus']
            
            # E-commerce platforms
            if any(platform in domain for platform in TRUSTED_PLATFORMS):
                score = max(score, TRUST_FACTORS['ecommerce_platform_min'])
            
            # Red flags
            if any(flag in domain or flag in path for flag in RED_FLAGS):
                score -= TRUST_FACTORS['red_flag_penalty']
            
            # Trusted TLDs
            if any(domain.endswith(tld) for tld in HIGH_TRUST_TLDS):
                score += TRUST_FACTORS['trusted_tld_bonus']
            
            # Clean domain names
            domain_parts = domain.split('.')
            if len(domain_parts) == 2 and len(domain_parts[0]) < 20:
                score += TRUST_FACTORS['clean_domain_bonus']
            
            return max(0.0, min(1.0, score))
        
        except Exception as e:
            return 0.3
    
    def add_trusted_domain(self, domain: str, score: float = 1.0):
        """Add a domain to the trusted domains list."""
        domain_clean = domain.replace('www.', '').lower()
        if domain_clean and domain_clean not in self.trust_scores:
            self.trust_scores[domain_clean] = score
            print(f"✅ Added {domain_clean} to trusted sources (score: {score:.2f})")
    
    def apply_frequency_boost(self, results: List[Dict]) -> List[Dict]:
        """
        Apply trust boost based on domain frequency.
        Domains appearing multiple times are more likely legitimate.
        
        Args:
            results: List of search results
            
        Returns:
            Updated results with frequency-based trust boost
        """
        if not results:
            return results
        
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
                    
                    # Determine boost
                    if count >= FREQUENCY_THRESHOLD_HIGH:
                        boost = FREQUENCY_BOOST_HIGH
                    elif count >= FREQUENCY_THRESHOLD_MED:
                        boost = FREQUENCY_BOOST_MED
                    else:
                        boost = 0.0
                    
                    result['trust_score'] = min(1.0, result.get('trust_score', 0) + boost)
                    result['frequency_boost'] = boost
                    result['domain_frequency'] = count
                except:
                    pass
        
        return results
    
    def get_trusted_domains(self) -> Dict[str, float]:
        """Get all known trusted domains and their scores."""
        return self.trust_scores.copy()

