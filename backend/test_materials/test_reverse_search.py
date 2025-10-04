#!/usr/bin/env python3
"""
Test script for Google Lens API counterfeit detection.
Uses Google Lens to find exact matches and visual matches for product authentication.
"""

import os
import sys
sys.path.append('..')
from generate_real_images import ReverseImageSearcher

def test_exact_matching():
    """Test Google Lens API for product matching and counterfeit detection"""
    
    # Check API key
    if not os.getenv('SERPAPI_API_KEY'):
        print("❌ SERPAPI_API_KEY environment variable not set!")
        print("Please set your SerpApi API key:")
        print("export SERPAPI_API_KEY='your_api_key_here'")
        return
    
    try:
        searcher = ReverseImageSearcher()
        
        print("🔍 Google Lens Product Authentication Test")
        print("="*60)
        print("Using Google Lens API for counterfeit detection")
        print("Searches for exact matches and visual matches")
        
        # Test with a sample image (Nike sneaker)
        test_url = "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400"
        print(f"\n🧪 Testing with: {test_url}")
        print("⏳ Searching with Google Lens...")
        
        # Search using Google Lens API
        results = searcher.search_by_image_url(test_url, max_results=15)
        
        if results:
            print(f"\n✅ Found {len(results)} results from Google Lens!")
            
            # Separate exact matches from visual matches
            exact_matches = [r for r in results if r.get('is_exact_match')]
            visual_matches = [r for r in results if not r.get('is_exact_match')]
            
            # Show section breakdown
            print(f"\n📊 RESULTS BREAKDOWN:")
            print("="*60)
            print(f"   🎯 Exact matches: {len(exact_matches)}")
            print(f"   👀 Visual matches: {len(visual_matches)}")
            
            # Analyze trust scores
            high_trust = [r for r in results if r['trust_score'] >= 0.8]
            medium_trust = [r for r in results if 0.5 <= r['trust_score'] < 0.8]
            low_trust = [r for r in results if r['trust_score'] < 0.5]
            
            print(f"\n🛡️  TRUST SCORE ANALYSIS:")
            print("="*60)
            print(f"   ✅ High trust (≥0.8): {len(high_trust)} results")
            print(f"   ⚠️  Medium trust (0.5-0.8): {len(medium_trust)} results")
            print(f"   ❌ Low trust (<0.5): {len(low_trust)} results")
            
            # Show top results
            print(f"\n🏆 TOP RESULTS:")
            print("="*80)
            
            for i, result in enumerate(results[:5], 1):
                match_type = "🎯 EXACT MATCH" if result.get('is_exact_match') else "👀 VISUAL MATCH"
                trust_indicator = "✅" if result['trust_score'] >= 0.8 else "⚠️" if result['trust_score'] >= 0.5 else "❌"
                
                print(f"\n{i}. {match_type}")
                print(f"   Title: {result['title']}")
                print(f"   {trust_indicator} Source: {result['source']} (Trust: {result['trust_score']:.2f})")
                print(f"   🔗 Link: {result['link']}")
                
                if result.get('price'):
                    print(f"   💰 Price: {result['price']}")
                if result.get('rating'):
                    print(f"   ⭐ Rating: {result['rating']}")
                if result.get('image_resolution'):
                    print(f"   📐 Resolution: {result['image_resolution']}")
            
            # Counterfeit detection insights
            print(f"\n🛡️  COUNTERFEIT DETECTION INSIGHTS:")
            print("="*60)
            
            if high_trust:
                print(f"\n✅ {len(high_trust)} HIGH-TRUST SOURCES FOUND:")
                print("   💡 These are verified authentic sources")
                for r in high_trust[:3]:
                    print(f"   • {r['source']} - {r['title'][:50]}")
                    print(f"     Link: {r['link']}")
            
            if exact_matches:
                print(f"\n🎯 {len(exact_matches)} EXACT MATCHES FOUND:")
                print("   💡 These are the exact same product")
                print("   ✅ Use these as reference for authentication")
                for r in exact_matches[:3]:
                    print(f"   • {r['title'][:60]}")
            
            if not high_trust and not exact_matches:
                print("\n⚠️  WARNING: No high-trust sources or exact matches found")
                print("   🚨 Higher risk of counterfeit")
                print("   💡 Recommendations:")
                print("   • Verify with official brand website")
                print("   • Check for authentication certificates")
                print("   • Compare physical details carefully")
            
        else:
            print("\n❌ No results found.")
            print("💡 This could indicate:")
            print("   • Very rare/unique item")
            print("   • Poor image quality")
            print("   • Item not widely available online")
            print("   • Potential counterfeit")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

def test_custom_exact_matching():
    """Test Google Lens with custom image URL"""
    print("\n🔗 Custom Image Google Lens Test")
    print("="*60)
    
    # Check API key
    if not os.getenv('SERPAPI_API_KEY'):
        print("❌ SERPAPI_API_KEY environment variable not set!")
        return
    
    try:
        searcher = ReverseImageSearcher()
        
        print("Enter an image URL to authenticate with Google Lens:")
        print("📸 Best results with:")
        print("   • Nike, Adidas, Jordan sneakers")
        print("   • Louis Vuitton, Gucci, Chanel handbags")
        print("   • Rolex, Omega, Cartier watches")
        print("   • Supreme, Off-White clothing")
        print("   • Collectible toys (Labubu, etc.)")
        
        image_url = input("\n🔗 Enter image URL: ").strip()
        
        if not image_url:
            print("❌ No URL provided")
            return
        
        if not image_url.startswith(('http://', 'https://')):
            print("❌ Please enter a valid HTTP/HTTPS URL")
            return
        
        print(f"\n🔍 Searching with Google Lens: {image_url}")
        print("⏳ This may take a few seconds...")
        
        results = searcher.search_by_image_url(image_url, max_results=15)
        
        if results:
            print(f"\n✅ Found {len(results)} results from Google Lens!")
            
            # Separate by match type
            exact_matches = [r for r in results if r.get('is_exact_match')]
            visual_matches = [r for r in results if not r.get('is_exact_match')]
            
            # Trust analysis
            high_trust = [r for r in results if r['trust_score'] >= 0.8]
            
            print(f"\n📊 QUICK SUMMARY:")
            print("="*60)
            print(f"   🎯 Exact matches: {len(exact_matches)}")
            print(f"   👀 Visual matches: {len(visual_matches)}")
            print(f"   ✅ High-trust sources: {len(high_trust)}")
            
            # Show top 5 results
            print(f"\n🏆 TOP 5 RESULTS:")
            print("="*80)
            
            for i, result in enumerate(results[:5], 1):
                match_type = "🎯 EXACT" if result.get('is_exact_match') else "👀 VISUAL"
                trust_emoji = "✅" if result['trust_score'] >= 0.8 else "⚠️" if result['trust_score'] >= 0.5 else "❌"
                
                print(f"\n{i}. [{match_type}] {result['title'][:60]}")
                print(f"   {trust_emoji} {result['source']} (Trust: {result['trust_score']:.2f})")
                print(f"   🔗 {result['link']}")
                
                if result.get('price'):
                    print(f"   💰 {result['price']}")
            
            # Authentication verdict
            print(f"\n🛡️  AUTHENTICATION VERDICT:")
            print("="*60)
            
            if high_trust and (exact_matches or len(visual_matches) >= 3):
                print("✅ LIKELY AUTHENTIC")
                print(f"   • Found {len(high_trust)} high-trust sources")
                if exact_matches:
                    print(f"   • Found {len(exact_matches)} exact matches")
                print("   • Product matches known authentic listings")
            elif high_trust or visual_matches:
                print("⚠️  NEEDS VERIFICATION")
                print("   • Some matches found, but limited high-trust sources")
                print("   • Compare physical details carefully")
                print("   • Check authentication certificates")
            else:
                print("🚨 SUSPICIOUS - HIGH RISK")
                print("   • No high-trust sources found")
                print("   • Limited or no matches")
                print("   • Recommend professional authentication")
            
        else:
            print("\n❌ No results found from Google Lens")
            print("⚠️  This is suspicious and could indicate:")
            print("   • Counterfeit item not available online")
            print("   • Very rare/unique item")
            print("   • Poor image quality affecting search")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print("🔍 Google Lens Counterfeit Detection System")
    print("="*60)
    print("Uses Google Lens API to authenticate products")
    print()
    
    # Check for API key first
    if not os.getenv('SERPAPI_API_KEY'):
        print("❌ SERPAPI_API_KEY environment variable not set!")
        print("\n📝 Setup Instructions:")
        print("1. Sign up at https://serpapi.com/")
        print("2. Get your API key from the dashboard")
        print("3. Set the environment variable:")
        print("   export SERPAPI_API_KEY='your_api_key_here'")
        print("\n💡 You get 100 free searches per month!")
        return
    
    print("✅ API key found!\n")
    
    # Ask user what they want to do
    print("Choose an option:")
    print("1. 🧪 Test with sample image (Nike sneaker)")
    print("2. 🔗 Test with custom image URL")
    print("3. 🎯 Run both tests")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            test_exact_matching()
        elif choice == "2":
            test_custom_exact_matching()
        elif choice == "3":
            test_exact_matching()
            test_custom_exact_matching()
        else:
            print("Invalid choice. Starting sample test...")
            test_exact_matching()
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
