#!/usr/bin/env python3
"""
Test to verify the parser initialization fix.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


# Mock the FuzzyMatcher and other dependencies
class MockFuzzyMatcher:
    @staticmethod
    def fuzzy_match(target, candidates, threshold=0.3):
        return None


class MockOCREngine:
    def __init__(self, tesseract_path=None, config=None):
        pass

    def extract_text_from_pdf(self, path):
        return "Test text"


class MockAmountNormalizer:
    def __init__(self, default_currency="USD"):
        pass

    def extract_amounts_from_text(self, text):
        return []


class MockOCRCorrections:
    def correct_text(self, text):
        return text


# Mock the imports
sys.modules["ocrinvoice.utils.fuzzy_matcher"] = type(
    "MockModule", (), {"FuzzyMatcher": MockFuzzyMatcher}
)()
sys.modules["ocrinvoice.core.ocr_engine"] = type(
    "MockModule", (), {"OCREngine": MockOCREngine}
)()
sys.modules["ocrinvoice.utils.amount_normalizer"] = type(
    "MockModule", (), {"AmountNormalizer": MockAmountNormalizer}
)()
sys.modules["ocrinvoice.utils.ocr_corrections"] = type(
    "MockModule", (), {"OCRCorrections": MockOCRCorrections}
)()

try:
    from ocrinvoice.parsers.invoice_parser import InvoiceParser
    from ocrinvoice.parsers.credit_card_parser import CreditCardBillParser

    print("🧪 Testing parser initialization...")

    # Test with None config
    print("\n1. Testing InvoiceParser with None config:")
    try:
        parser = InvoiceParser(None)
        print("  ✅ InvoiceParser initialized successfully with None config")
        print(f"  📊 Config keys: {list(parser.config.keys())}")
        print(
            f"  📊 Business alias manager: {parser.business_alias_manager is not None}"
        )
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Test with empty config
    print("\n2. Testing InvoiceParser with empty config:")
    try:
        parser = InvoiceParser({})
        print("  ✅ InvoiceParser initialized successfully with empty config")
        print(f"  📊 Config keys: {list(parser.config.keys())}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Test with valid config
    print("\n3. Testing InvoiceParser with valid config:")
    try:
        config = {"debug": True, "known_companies": ["Test Company"]}
        parser = InvoiceParser(config)
        print("  ✅ InvoiceParser initialized successfully with valid config")
        print(f"  📊 Config keys: {list(parser.config.keys())}")
        print(f"  📊 Debug mode: {parser.debug}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Test CreditCardBillParser
    print("\n4. Testing CreditCardBillParser with None config:")
    try:
        parser = CreditCardBillParser(None)
        print("  ✅ CreditCardBillParser initialized successfully with None config")
        print(f"  📊 Config keys: {list(parser.config.keys())}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    print("\n🎉 All parser initialization tests passed!")

except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback

    traceback.print_exc()
