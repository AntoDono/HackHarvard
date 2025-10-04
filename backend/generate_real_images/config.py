"""
Configuration for counterfeit detection system.

Contains brand mappings, trust scores, and system constants.
"""

from typing import Dict

# Known brand mappings: brand keyword -> official website
KNOWN_BRANDS: Dict[str, str] = {
    # Sneakers & Athletic
    'nike': 'nike.com',
    'jordan': 'nike.com',
    'air jordan': 'nike.com',
    'adidas': 'adidas.com',
    'yeezy': 'adidas.com/yeezy',
    'new balance': 'newbalance.com',
    'converse': 'converse.com',
    'vans': 'vans.com',
    'puma': 'puma.com',
    'reebok': 'reebok.com',
    'asics': 'asics.com',
    'under armour': 'underarmour.com',
    
    # Luxury Fashion
    'louis vuitton': 'louisvuitton.com',
    'lv': 'louisvuitton.com',
    'gucci': 'gucci.com',
    'chanel': 'chanel.com',
    'prada': 'prada.com',
    'hermes': 'hermes.com',
    'hermès': 'hermes.com',
    'balenciaga': 'balenciaga.com',
    'burberry': 'burberry.com',
    'versace': 'versace.com',
    'fendi': 'fendi.com',
    'dior': 'dior.com',
    'saint laurent': 'ysl.com',
    'ysl': 'ysl.com',
    'bottega veneta': 'bottegaveneta.com',
    'givenchy': 'givenchy.com',
    'alexander mcqueen': 'alexandermcqueen.com',
    
    # Watches
    'rolex': 'rolex.com',
    'omega': 'omegawatches.com',
    'cartier': 'cartier.com',
    
    # Streetwear
    'supreme': 'supremenewyork.com',
    'off-white': 'off---white.com',
    
    # Collectibles
    'labubu': 'how2work.com',
    'pop mart': 'popmart.com',
    
    # Outdoor
    'the north face': 'thenorthface.com',
    'patagonia': 'patagonia.com',
}

# Hardcoded trust scores for known domains
TRUST_SCORES: Dict[str, float] = {
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

# Dynamic trust scoring factors
TRUST_FACTORS = {
    'https_bonus': 0.1,
    'official_keyword_bonus': 0.15,
    'ecommerce_platform_min': 0.5,
    'red_flag_penalty': 0.3,
    'trusted_tld_bonus': 0.05,
    'clean_domain_bonus': 0.05,
}

# Official indicators in domain names
OFFICIAL_INDICATORS = [
    'official', 'store', 'shop', 'retail', 'direct',
    'authentic', 'authorized', 'certified'
]

# E-commerce platforms
TRUSTED_PLATFORMS = [
    'shopify.com', 'bigcommerce.com', 'wix.com', 'squarespace.com',
    'myshopify.com', 'ebay.', 'amazon.', 'walmart.', 'target.com'
]

# Red flag keywords
RED_FLAGS = [
    'replica', 'fake', 'knock-off', 'knockoff', 'copy',
    'cheap', 'discount', 'wholesale', 'bulk'
]

# Trusted TLDs
HIGH_TRUST_TLDS = ['.com', '.org', '.net', '.gov', '.edu']

# Similarity scoring keywords
EXACT_MATCH_KEYWORDS = [
    'product', 'item', 'model', 'sku', 'part number', 'serial',
    'authentic', 'genuine', 'original', 'official', 'brand'
]

GENERIC_KEYWORDS = [
    'similar', 'like', 'related', 'compare', 'alternative',
    'style', 'type', 'category', 'collection'
]

# Frequency boost thresholds
FREQUENCY_BOOST_HIGH = 0.15  # 3+ appearances
FREQUENCY_BOOST_MED = 0.08   # 2 appearances
FREQUENCY_THRESHOLD_HIGH = 3
FREQUENCY_THRESHOLD_MED = 2

