#!/usr/bin/env python3
"""
Test script for automatic backup functionality.
"""

import sys
import os
import json
import tempfile
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.ocrinvoice.business.business_mapping_manager import BusinessMappingManager


def test_auto_backup_functionality():
    """Test automatic backup functionality."""
    print("🧪 Testing Automatic Backup Functionality")
    print("=" * 60)

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Using temporary directory: {temp_dir}")
        
        # Create a test mapping file
        test_mapping_file = os.path.join(temp_dir, "test_business_mappings.json")
        test_config = {
            "official_names": ["test-company-1", "test-company-2"],
            "exact_matches": {
                "test1": "test-company-1",
                "test2": "test-company-2"
            },
            "partial_matches": {
                "partial1": "test-company-1"
            },
            "fuzzy_candidates": ["test-company-1", "test-company-2"],
            "indicators": {
                "test-company-1": ["test", "company"]
            },
            "confidence_weights": {
                "exact_match": 1.0,
                "partial_match": 0.8,
                "fuzzy_match": 0.6
            }
        }
        
        with open(test_mapping_file, "w", encoding="utf-8") as f:
            json.dump(test_config, f, indent=4)
        
        print("✅ Created test mapping file")
        
        # Initialize manager with test file
        manager = BusinessMappingManager(test_mapping_file)
        print(f"✅ Initialized manager with {len(manager.get_official_names())} official names")
        
        # Test startup backup
        print("\n🚀 Testing startup backup...")
        startup_backup = manager.create_startup_backup()
        if startup_backup:
            print(f"✅ Startup backup created: {os.path.basename(startup_backup)}")
        else:
            print("❌ Startup backup failed")
            return False
        
        # Test creating multiple backups to trigger cleanup
        print("\n📦 Creating multiple backups to test cleanup...")
        backup_paths = []
        for i in range(15):  # Create 15 backups (more than the 10 limit)
            backup_path = manager.create_backup()
            backup_paths.append(backup_path)
            print(f"   Created backup {i+1}: {os.path.basename(backup_path)}")
            time.sleep(0.1)  # Small delay to ensure unique timestamps
        
        # Check how many backups exist after cleanup
        remaining_backups = manager.list_backups()
        print(f"\n📋 Remaining backups after cleanup: {len(remaining_backups)}")
        
        if len(remaining_backups) <= 10:
            print("✅ Cleanup working correctly - keeping only recent backups")
        else:
            print(f"❌ Cleanup failed - {len(remaining_backups)} backups remain (should be ≤10)")
            return False
        
        # Test shutdown backup
        print("\n🛑 Testing shutdown backup...")
        shutdown_backup = manager.create_shutdown_backup()
        if shutdown_backup:
            print(f"✅ Shutdown backup created: {os.path.basename(shutdown_backup)}")
        else:
            print("❌ Shutdown backup failed")
            return False
        
        # Check final backup count
        final_backups = manager.list_backups()
        print(f"\n📋 Final backup count: {len(final_backups)}")
        
        if len(final_backups) <= 10:
            print("✅ Final cleanup working correctly")
        else:
            print(f"❌ Final cleanup failed - {len(final_backups)} backups remain")
            return False
        
        print("\n✅ All automatic backup tests passed!")
        return True


def test_backup_cleanup_edge_cases():
    """Test backup cleanup edge cases."""
    print("\n🧪 Testing Backup Cleanup Edge Cases")
    print("=" * 60)

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Using temporary directory: {temp_dir}")
        
        # Create a test mapping file
        test_mapping_file = os.path.join(temp_dir, "test_business_mappings.json")
        test_config = {
            "official_names": ["test-company"],
            "exact_matches": {},
            "partial_matches": {},
            "fuzzy_candidates": [],
            "indicators": {},
            "confidence_weights": {
                "exact_match": 1.0,
                "partial_match": 0.8,
                "fuzzy_match": 0.6
            }
        }
        
        with open(test_mapping_file, "w", encoding="utf-8") as f:
            json.dump(test_config, f, indent=4)
        
        # Initialize manager with test file
        manager = BusinessMappingManager(test_mapping_file)
        
        # Test cleanup with no backups
        print("\n📋 Testing cleanup with no backups...")
        deleted_count = manager.cleanup_old_backups(keep_count=10)
        if deleted_count == 0:
            print("✅ Correctly handled no backups")
        else:
            print(f"❌ Unexpected deletion count: {deleted_count}")
            return False
        
        # Test cleanup with exactly 10 backups
        print("\n📋 Testing cleanup with exactly 10 backups...")
        for i in range(10):
            manager.create_backup()
            time.sleep(0.1)
        
        deleted_count = manager.cleanup_old_backups(keep_count=10)
        if deleted_count == 0:
            print("✅ Correctly kept all 10 backups")
        else:
            print(f"❌ Unexpected deletion count: {deleted_count}")
            return False
        
        # Test cleanup with custom keep count
        print("\n📋 Testing cleanup with custom keep count (5)...")
        for i in range(3):  # Add 3 more backups
            manager.create_backup()
            time.sleep(0.1)
        
        deleted_count = manager.cleanup_old_backups(keep_count=5)
        remaining_backups = manager.list_backups()
        
        if len(remaining_backups) == 5:
            print("✅ Custom keep count working correctly")
        else:
            print(f"❌ Custom keep count failed - {len(remaining_backups)} backups remain")
            return False
        
        print("\n✅ All edge case tests passed!")
        return True


def test_backup_file_integrity():
    """Test that backup files maintain data integrity."""
    print("\n🧪 Testing Backup File Integrity")
    print("=" * 60)

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Using temporary directory: {temp_dir}")
        
        # Create a test mapping file with complex data
        test_mapping_file = os.path.join(temp_dir, "test_business_mappings.json")
        test_config = {
            "official_names": ["company-1", "company-2", "company-3"],
            "exact_matches": {
                "alias1": "company-1",
                "alias2": "company-2"
            },
            "partial_matches": {
                "partial1": "company-1",
                "partial2": "company-3"
            },
            "fuzzy_candidates": ["company-1", "company-2"],
            "indicators": {
                "company-1": ["indicator1", "indicator2"],
                "company-2": ["indicator3"]
            },
            "confidence_weights": {
                "exact_match": 1.0,
                "partial_match": 0.8,
                "fuzzy_match": 0.6
            }
        }
        
        with open(test_mapping_file, "w", encoding="utf-8") as f:
            json.dump(test_config, f, indent=4)
        
        # Initialize manager with test file
        manager = BusinessMappingManager(test_mapping_file)
        
        # Create startup backup
        print("📦 Creating startup backup...")
        startup_backup = manager.create_startup_backup()
        
        if not startup_backup:
            print("❌ Startup backup failed")
            return False
        
        # Verify backup content matches original
        print("🔍 Verifying backup content...")
        with open(startup_backup, "r", encoding="utf-8") as f:
            backup_config = json.load(f)
        
        # Check that all keys are present
        for key in test_config.keys():
            if key not in backup_config:
                print(f"❌ Missing key in backup: {key}")
                return False
        
        # Check that data matches
        if backup_config == test_config:
            print("✅ Backup content matches original exactly")
        else:
            print("❌ Backup content does not match original")
            return False
        
        # Test restore from backup
        print("🔄 Testing restore from backup...")
        success = manager.restore_backup(startup_backup)
        
        if success:
            print("✅ Restore from backup successful")
            
            # Verify restored content
            if manager.config == test_config:
                print("✅ Restored content matches original")
            else:
                print("❌ Restored content does not match original")
                return False
        else:
            print("❌ Restore from backup failed")
            return False
        
        print("\n✅ All integrity tests passed!")
        return True


if __name__ == "__main__":
    print("🚀 Starting Automatic Backup Tests")
    print("=" * 60)
    
    success = True
    
    # Run tests
    if not test_auto_backup_functionality():
        success = False
    
    if not test_backup_cleanup_edge_cases():
        success = False
    
    if not test_backup_file_integrity():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All automatic backup tests passed!")
    else:
        print("❌ Some automatic backup tests failed!")
    
    sys.exit(0 if success else 1) 