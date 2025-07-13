#!/usr/bin/env python3
"""
Test script for official names functionality.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.ocrinvoice.business.business_mapping_manager import BusinessMappingManager


def test_official_names_operations():
    """Test official names operations."""
    print("🧪 Testing Official Names Operations")
    print("=" * 50)

    # Initialize manager
    manager = BusinessMappingManager()

    # Get current official names
    print("📋 Current official names:")
    current_names = manager.get_official_names()
    for name in current_names:
        print(f"  - {name}")
    print()

    # Test adding a new official name
    test_name = "test-official-name-new"
    print(f"➕ Adding official name: {test_name}")
    success = manager.add_official_name(test_name)
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")

    # Test adding the same name again (should fail)
    print(f"➕ Adding duplicate official name: {test_name}")
    success = manager.add_official_name(test_name)
    print(f"   Result: {'✅ Success' if success else '❌ Failed (expected)'}")

    # Test updating an official name
    old_name = test_name
    new_name = "test-official-name-updated"
    print(f"✏️ Updating official name: {old_name} → {new_name}")
    success = manager.update_official_name(old_name, new_name)
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")

    # Test updating to an existing name (should fail)
    print(
        f"✏️ Updating to existing name: {new_name} → {current_names[0] if current_names else 'test'}"
    )
    success = manager.update_official_name(
        new_name, current_names[0] if current_names else "test"
    )
    print(f"   Result: {'✅ Success' if success else '❌ Failed (expected)'}")

    # Test removing the test official name
    print(f"🗑️ Removing official name: {new_name}")
    success = manager.remove_official_name(new_name)
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")

    # Test removing a non-existent name (should fail)
    print("🗑️ Removing non-existent name: non-existent-name")
    success = manager.remove_official_name("non-existent-name")
    print(f"   Result: {'✅ Success' if success else '❌ Failed (expected)'}")

    print("\n✅ Official names operations test completed!")


def test_official_names_with_aliases():
    """Test official names with alias mappings."""
    print("\n🧪 Testing Official Names with Aliases")
    print("=" * 50)

    # Initialize manager
    manager = BusinessMappingManager()

    # Add a test official name
    test_official = "test-official-with-aliases"
    manager.add_official_name(test_official)

    # Add some aliases that reference this official name
    print(f"➕ Adding aliases for: {test_official}")

    # Add to exact matches
    manager.add_mapping("test-company-exact", test_official, "exact_matches")
    print(f"   ✅ Added exact match: test-company-exact → {test_official}")

    # Add to partial matches
    manager.add_mapping("test-company-partial", test_official, "partial_matches")
    print(f"   ✅ Added partial match: test-company-partial → {test_official}")

    # Add to fuzzy candidates
    manager.add_mapping(test_official, test_official, "fuzzy_candidates")
    print(f"   ✅ Added fuzzy candidate: {test_official}")

    # Now update the official name
    new_official = "test-official-updated-with-aliases"
    print(f"\n✏️ Updating official name: {test_official} → {new_official}")
    success = manager.update_official_name(test_official, new_official)
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")

    # Check if aliases were updated
    print("\n📋 Checking if aliases were updated:")
    exact_matches = manager.config.get("exact_matches", {})
    partial_matches = manager.config.get("partial_matches", {})
    fuzzy_candidates = manager.config.get("fuzzy_candidates", [])

    if (
        "test-company-exact" in exact_matches
        and exact_matches["test-company-exact"] == new_official
    ):
        print("   ✅ Exact match updated correctly")
    else:
        print("   ❌ Exact match not updated correctly")

    if (
        "test-company-partial" in partial_matches
        and partial_matches["test-company-partial"] == new_official
    ):
        print("   ✅ Partial match updated correctly")
    else:
        print("   ❌ Partial match not updated correctly")

    if new_official in fuzzy_candidates:
        print("   ✅ Fuzzy candidate updated correctly")
    else:
        print("   ❌ Fuzzy candidate not updated correctly")

    # Clean up
    manager.remove_official_name(new_official)
    print(f"\n🗑️ Cleaned up test official name: {new_official}")

    print("\n✅ Official names with aliases test completed!")


if __name__ == "__main__":
    test_official_names_operations()
    test_official_names_with_aliases()
