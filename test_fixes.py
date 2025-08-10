#!/usr/bin/env python3
"""Test script to verify the timeout and context window fixes."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import scrape_urls

# Test URLs that were previously failing
test_urls = [
    "https://basewealthmanagement.com/client-services/",
    "https://www.michaelbradyco.com/meet-the-team"
]

# Fields to extract (same as in streamlit app)
fields_to_extract = [
    "company location",
    "company overview", 
    "investment criteria",
    "investment strategy",
    "portfolio companies",
    "team/leadership"
]

def test_scraper():
    """Test the scraper with problematic URLs."""
    print("Testing scraper fixes with problematic URLs...")
    print("=" * 50)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\nTest {i}/2: {url}")
        print("-" * 40)
        
        try:
            # Test with a single URL at a time
            results, token_counts, cost = scrape_urls([url], fields_to_extract, "gpt-4o-mini")
            
            # Check results
            if url in results:
                result = results[url]
                if "error" in result:
                    print(f"❌ FAILED: {result['error']}")
                else:
                    print(f"✅ SUCCESS: Data extracted successfully")
                    print(f"   Input tokens: {token_counts['input_tokens']}")
                    print(f"   Output tokens: {token_counts['output_tokens']}")
                    print(f"   Cost: ${cost:.4f}")
                    
                    # Show sample extracted data
                    if isinstance(result, dict) and result:
                        print(f"   Sample data keys: {list(result.keys())[:3]}...")
            else:
                print(f"❌ FAILED: No result returned for URL")
                
        except Exception as e:
            print(f"❌ FAILED: Exception occurred: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Test complete.")

if __name__ == "__main__":
    test_scraper()