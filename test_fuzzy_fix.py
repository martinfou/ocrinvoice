#!/usr/bin/env python3
"""Test script to verify the fuzzy_match fix."""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_fuzzy_match():
    """Test the fuzzy_match static method."""
    try:
        from ocrinvoice.utils.fuzzy_matcher import FuzzyMatcher
        
        # Test the static method
        result = FuzzyMatcher.fuzzy_match('test', ['test', 'other'], 0.8)
        print(f"✅ fuzzy_match works: {result}")
        
        # Test with no match
        result2 = FuzzyMatcher.fuzzy_match('xyz', ['test', 'other'], 0.8)
        print(f"✅ fuzzy_match no match: {result2}")
        
        # Test with empty inputs
        result3 = FuzzyMatcher.fuzzy_match('', ['test'], 0.8)
        print(f"✅ fuzzy_match empty target: {result3}")
        
        print("🎉 All fuzzy_match tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fuzzy_match() 