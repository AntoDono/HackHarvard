# Counterfeit Detector Package

A modular, production-ready system for detecting counterfeit products using Google Lens API, dynamic trust scoring, and automatic brand identification.

## 📁 Package Structure

```
counterfeit_detector/
├── __init__.py           # Package initialization and exports
├── config.py             # Configuration, constants, and brand database
├── brand_detector.py     # Brand identification from search results
├── trust_scorer.py       # Dynamic trust scoring system
├── image_searcher.py     # Main Google Lens API integration
├── utils.py              # Utility functions
└── README.md             # This file
```

## 🎯 Module Overview

### 1. `config.py` - Configuration
Contains all system constants and configurations:
- **KNOWN_BRANDS**: 40+ brand mappings (brand → official website)
- **TRUST_SCORES**: Hardcoded trust scores for known domains
- **TRUST_FACTORS**: Dynamic scoring parameters
- **Keywords**: For similarity scoring and filtering

**Why separate?**
- Easy to update brands without touching code
- Centralized configuration management
- Can be replaced with external config files (JSON/YAML)

### 2. `brand_detector.py` - Brand Detection
Automatically identifies brands from search results.

**Key Features:**
- Scans knowledge graphs, exact matches, visual matches
- Prioritizes by confidence level (1.0, 0.95, 0.7)
- Maps brands to official websites
- 40+ supported brands across categories

**Example:**
```python
from counterfeit_detector import BrandDetector

detector = BrandDetector()
brand_info = detector.identify_from_lens_results(lens_data)
# Returns: {'name': 'Nike', 'official_website': 'nike.com', 'confidence': 0.95}
```

### 3. `trust_scorer.py` - Trust Scoring
Calculates trust scores using hardcoded + dynamic analysis.

**Scoring Factors:**
- Hardcoded scores for known brands (0.8-1.0)
- HTTPS vs HTTP (+0.1)
- Official keywords in domain (+0.15)
- E-commerce platforms (0.5 minimum)
- Red flags (-0.3)
- Domain frequency boost (+0.08 to +0.15)

**Example:**
```python
from counterfeit_detector import TrustScorer

scorer = TrustScorer()
trust = scorer.get_domain_trust_score("https://nike.com")
# Returns: 1.0
```

### 4. `image_searcher.py` - Main API
Primary interface for reverse image search.

**Key Features:**
- Google Lens API integration
- Automatic brand detection
- Trust scoring application
- Result filtering and ranking

**Example:**
```python
from counterfeit_detector import ReverseImageSearcher

searcher = ReverseImageSearcher()
results = searcher.search_by_image_url(image_url)
# Returns: List of results with trust scores, brand info, prices
```

### 5. `utils.py` - Utilities
Helper functions for common tasks.

**Functions:**
- `calculate_similarity_score()`: Keyword-based similarity
- `extract_domain()`: Clean domain extraction
- `is_valid_url()`: URL validation

## 🚀 Usage Examples

### Basic Search
```python
from counterfeit_detector import ReverseImageSearcher

searcher = ReverseImageSearcher(api_key="your_key")
results = searcher.search_by_image_url(
    "https://example.com/product.jpg",
    max_results=10
)

for result in results:
    print(f"{result['title']}")
    print(f"Trust: {result['trust_score']:.2f}")
    print(f"Brand: {result.get('detected_brand', 'Unknown')}")
```

### Filter by Trust
```python
# Get only high-trust results (≥0.8)
high_trust = searcher.get_high_trust_results(results)

# Get official brand website results
official = searcher.get_official_results(results)

# Custom filter
trusted = searcher.filter_by_trust_score(results, min_trust=0.7)
```

### Standalone Brand Detection
```python
from counterfeit_detector import BrandDetector

detector = BrandDetector()

# Check if brand is known
if detector.is_known_brand("Nike"):
    website = detector.get_official_website("Nike")
    print(f"Official site: {website}")
```

### Standalone Trust Scoring
```python
from counterfeit_detector import TrustScorer

scorer = TrustScorer()

# Score a single URL
trust = scorer.get_domain_trust_score("https://example.com")

# Add custom trusted domain
scorer.add_trusted_domain("newbrand.com", score=1.0)

# Apply frequency boosting to results
boosted_results = scorer.apply_frequency_boost(results)
```

## 📦 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export SERPAPI_API_KEY='your_key_here'

# Import in Python
from counterfeit_detector import ReverseImageSearcher
```

## 🔧 Configuration

### Adding New Brands
Edit `config.py`:
```python
KNOWN_BRANDS = {
    ...
    'new brand': 'newbrand.com',
}

TRUST_SCORES = {
    ...
    'newbrand.com': 1.0,
}
```

### Adjusting Trust Factors
Edit `config.py`:
```python
TRUST_FACTORS = {
    'https_bonus': 0.1,          # Increase for more HTTPS weight
    'red_flag_penalty': 0.3,     # Increase to penalize red flags more
    ...
}
```

## 🧪 Testing

```bash
# Test main functionality
python generate_real_images_new.py

# Test brand detection
python test_materials/test_brand_detection.py

# Test trust scoring
python test_materials/test_dynamic_trust.py
```

## 📊 Benefits of Modular Design

### 1. **Maintainability**
- Each module has a single responsibility
- Easy to locate and fix bugs
- Changes don't ripple across codebase

### 2. **Testability**
- Each module can be tested independently
- Mock dependencies easily
- Unit tests are straightforward

### 3. **Reusability**
- Use `BrandDetector` in other projects
- Share `TrustScorer` across services
- Mix and match components

### 4. **Scalability**
- Add new modules without touching existing code
- Replace modules with improved versions
- Plug in external services (databases, APIs)

### 5. **Collaboration**
- Multiple developers can work on different modules
- Clear interfaces between components
- Less merge conflicts

## 🔄 Migration from Old Code

Old code still works via backward-compatible wrapper:
```python
# This still works
from generate_real_images import ReverseImageSearcher

# This is the new way
from counterfeit_detector import ReverseImageSearcher
```

Both import the same class, so no code changes needed!

## 📝 Future Enhancements

### Easy to Add:
1. **Database Module** (`database.py`)
   - Store search history
   - Cache results
   - Track authentication verdicts

2. **API Module** (`api.py`)
   - FastAPI integration
   - REST endpoints
   - Authentication

3. **ML Module** (`ml_detector.py`)
   - Visual similarity using CLIP
   - Logo detection
   - OCR for serial numbers

4. **Report Module** (`reporter.py`)
   - Generate PDF certificates
   - Email notifications
   - Analytics dashboard

## 📄 License

Part of the HackHarvard Counterfeit Detection project.

## 🤝 Contributing

To add a new module:
1. Create `new_module.py` in `counterfeit_detector/`
2. Add to `__init__.py` exports
3. Update this README
4. Add tests in `test_materials/`

## 📧 Support

For issues or questions, check:
- Documentation in each module
- Test files for examples
- This README for overview

