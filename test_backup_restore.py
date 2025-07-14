#!/usr/bin/env python3
"""
Test script for backup and restore functionality.
"""

import sys
import os
import json
import tempfile
import shutil
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.ocrinvoice.business.business_mapping_manager import BusinessMappingManager


def test_backup_restore_functionality():
    """Test backup and restore functionality."""
    print("🧪 Testing Backup and Restore Functionality")
    print("=" * 60)

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Using temporary directory: {temp_dir}")

        # Create a test mapping file
        test_mapping_file = os.path.join(temp_dir, "test_business_mappings.json")
        test_config = {
            "official_names": ["test-company-1", "test-company-2"],
            "exact_matches": {"test1": "test-company-1", "test2": "test-company-2"},
            "partial_matches": {"partial1": "test-company-1"},
            "fuzzy_candidates": ["test-company-1"],
            "indicators": {"test-company-1": ["test", "company"]},
            "confidence_weights": {
                "exact_match": 1.0,
                "partial_match": 0.8,
                "fuzzy_match": 0.6,
            },
        }

        with open(test_mapping_file, "w", encoding="utf-8") as f:
            json.dump(test_config, f, indent=4)

        print("✅ Created test mapping file")

        # Initialize manager with test file
        manager = BusinessMappingManager(test_mapping_file)
        print(
            f"✅ Initialized manager with {len(manager.get_official_names())} official names"
        )

        # Test creating backup
        print("\n📦 Testing backup creation...")
        backup_path = manager.create_backup()
        print(f"✅ Backup created: {backup_path}")

        # Verify backup file exists and has correct content
        if os.path.exists(backup_path):
            with open(backup_path, "r", encoding="utf-8") as f:
                backup_config = json.load(f)

            if backup_config == test_config:
                print("✅ Backup content matches original configuration")
            else:
                print("❌ Backup content does not match original configuration")
                return False
        else:
            print("❌ Backup file was not created")
            return False

        # Test listing backups
        print("\n📋 Testing backup listing...")
        backup_files = manager.list_backups()
        print(f"✅ Found {len(backup_files)} backup files")

        if len(backup_files) > 0:
            print(f"   Latest backup: {os.path.basename(backup_files[0])}")

        # Test getting backup info
        print("\nℹ️ Testing backup info...")
        if backup_files:
            backup_info = manager.get_backup_info(backup_files[0])
            if backup_info:
                print(f"✅ Backup info retrieved:")
                print(f"   File size: {backup_info['file_size']} bytes")
                print(f"   Official names: {backup_info['official_names_count']}")
                print(f"   Exact matches: {backup_info['exact_matches_count']}")
                print(f"   Partial matches: {backup_info['partial_matches_count']}")
            else:
                print("❌ Failed to get backup info")
                return False

        # Test modifying configuration
        print("\n✏️ Testing configuration modification...")
        manager.add_official_name("test-company-3")
        manager.add_mapping("test3", "test-company-3", "exact_matches")

        current_official_names = manager.get_official_names()
        print(
            f"✅ Modified configuration: {len(current_official_names)} official names"
        )

        # Test restoring from backup
        print("\n🔄 Testing backup restore...")
        success = manager.restore_backup(backup_path)

        if success:
            print("✅ Backup restored successfully")

            # Verify configuration was restored
            restored_official_names = manager.get_official_names()
            if (
                len(restored_official_names) == 2
                and "test-company-3" not in restored_official_names
            ):
                print("✅ Configuration correctly restored to original state")
            else:
                print("❌ Configuration was not correctly restored")
                return False
        else:
            print("❌ Failed to restore backup")
            return False

        # Test creating backup with custom path
        print("\n📁 Testing custom backup path...")
        custom_backup_path = os.path.join(temp_dir, "custom_backup.json")
        custom_backup = manager.create_backup(custom_backup_path)

        if custom_backup == custom_backup_path and os.path.exists(custom_backup_path):
            print("✅ Custom backup created successfully")
        else:
            print("❌ Failed to create custom backup")
            return False

        # Test invalid backup file
        print("\n🚫 Testing invalid backup file...")
        invalid_backup_path = os.path.join(temp_dir, "invalid_backup.json")
        with open(invalid_backup_path, "w") as f:
            f.write("invalid json content")

        success = manager.restore_backup(invalid_backup_path)
        if not success:
            print("✅ Correctly rejected invalid backup file")
        else:
            print("❌ Should have rejected invalid backup file")
            return False

        # Test non-existent backup file
        print("\n🚫 Testing non-existent backup file...")
        success = manager.restore_backup("non_existent_file.json")
        if not success:
            print("✅ Correctly rejected non-existent backup file")
        else:
            print("❌ Should have rejected non-existent backup file")
            return False

        print("\n✅ All backup and restore tests passed!")
        return True


def test_backup_directory_creation():
    """Test that backup directory is created automatically."""
    print("\n🧪 Testing Backup Directory Creation")
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
                "fuzzy_match": 0.6,
            },
        }

        with open(test_mapping_file, "w", encoding="utf-8") as f:
            json.dump(test_config, f, indent=4)

        # Initialize manager
        manager = BusinessMappingManager(test_mapping_file)

        # Check if backup directory exists
        backup_dir = Path(test_mapping_file).parent / "backups"
        print(f"📁 Backup directory path: {backup_dir}")

        if not backup_dir.exists():
            print("📁 Backup directory does not exist yet")

        # Create backup (should create directory)
        backup_path = manager.create_backup()
        print(f"✅ Backup created: {backup_path}")

        if backup_dir.exists():
            print("✅ Backup directory was created automatically")
        else:
            print("❌ Backup directory was not created")
            return False

        # Check backup directory contents
        backup_files = list(backup_dir.glob("business_mappings_backup_*.json"))
        print(f"✅ Found {len(backup_files)} backup files in directory")

        return True


def test_backup_file_naming():
    """Test backup file naming convention."""
    print("\n🧪 Testing Backup File Naming")
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
                "fuzzy_match": 0.6,
            },
        }

        with open(test_mapping_file, "w", encoding="utf-8") as f:
            json.dump(test_config, f, indent=4)

        # Initialize manager
        manager = BusinessMappingManager(test_mapping_file)

        # Create multiple backups
        backup_paths = []
        for i in range(3):
            backup_path = manager.create_backup()
            backup_paths.append(backup_path)
            print(f"✅ Created backup {i+1}: {os.path.basename(backup_path)}")
            time.sleep(0.1)  # Small delay to ensure unique timestamps

        # Verify naming convention
        for backup_path in backup_paths:
            filename = os.path.basename(backup_path)
            if filename.startswith("business_mappings_backup_") and filename.endswith(
                ".json"
            ):
                print(f"✅ Backup file follows naming convention: {filename}")
            else:
                print(f"❌ Backup file does not follow naming convention: {filename}")
                return False

        # Test listing backups (should be sorted by time)
        backup_files = manager.list_backups()
        print(f"✅ Listed {len(backup_files)} backup files")

        if len(backup_files) >= 3:
            print("✅ Backup listing works correctly")
        else:
            print("❌ Backup listing failed")
            return False

        return True


if __name__ == "__main__":
    print("🚀 Starting Backup and Restore Tests")
    print("=" * 60)

    success = True

    # Run tests
    if not test_backup_restore_functionality():
        success = False

    if not test_backup_directory_creation():
        success = False

    if not test_backup_file_naming():
        success = False

    print("\n" + "=" * 60)
    if success:
        print("🎉 All backup and restore tests passed!")
    else:
        print("❌ Some backup and restore tests failed!")

    sys.exit(0 if success else 1)
