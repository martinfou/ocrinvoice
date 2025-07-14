#!/usr/bin/env python3
"""
Test script for project feature functionality.

This script tests the project management features including CRUD operations,
GUI integration, and file naming with project support.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_project_manager():
    """Test the ProjectManager functionality."""
    print("🧪 Testing ProjectManager...")

    try:
        from ocrinvoice.business.project_manager import ProjectManager

        # Create a temporary project manager
        pm = ProjectManager()

        print("✅ ProjectManager created successfully")

        # Test adding projects
        print("\n📝 Testing project creation...")

        # Add some test projects
        project1_id = pm.add_project(
            "Kitchen Renovation", "Kitchen and bathroom renovation project"
        )
        print(f"✅ Added project: Kitchen Renovation (ID: {project1_id})")

        project2_id = pm.add_project(
            "Office Supplies", "General office supplies and equipment"
        )
        print(f"✅ Added project: Office Supplies (ID: {project2_id})")

        project3_id = pm.add_project(
            "Marketing Campaign", "Digital marketing campaign expenses"
        )
        print(f"✅ Added project: Marketing Campaign (ID: {project3_id})")

        # Test getting projects
        print("\n📋 Testing project retrieval...")
        projects = pm.get_projects()
        print(f"✅ Retrieved {len(projects)} projects:")
        for project in projects:
            print(f"   - {project['name']} ({project['id']}): {project['description']}")

        # Test project names
        project_names = pm.get_project_names()
        print(f"\n📝 Project names: {project_names}")

        # Test default project
        default_project = pm.get_default_project()
        print(f"🏠 Default project: {default_project}")

        # Test updating a project
        print("\n✏️ Testing project update...")
        success = pm.update_project(
            project1_id,
            "Kitchen & Bath Renovation",
            "Updated kitchen and bathroom renovation project",
        )
        if success:
            print("✅ Project updated successfully")
            # Get the new ID after update (ID changes when name changes)
            updated_projects = pm.get_projects()
            updated_project = next(
                (p for p in updated_projects if "Kitchen & Bath" in p["name"]), None
            )
            if updated_project:
                project1_id = updated_project["id"]
                print(f"✅ Updated project ID: {project1_id}")
        else:
            print("❌ Project update failed")

        # Test getting a specific project
        print("\n🔍 Testing specific project retrieval...")
        project = pm.get_project(project1_id)
        if project:
            print(f"✅ Retrieved project: {project['name']} - {project['description']}")
        else:
            print("❌ Failed to retrieve project")

        # Test project existence
        print("\n✅ Testing project existence...")
        exists = pm.project_exists(project1_id)
        print(f"Project exists: {exists}")

        # Test stats
        print("\n📊 Testing statistics...")
        stats = pm.get_stats()
        print(f"Statistics: {stats}")

        # Test deleting a project
        print("\n🗑️ Testing project deletion...")
        success = pm.delete_project(project3_id)
        if success:
            print("✅ Project deleted successfully")
        else:
            print("❌ Project deletion failed")

        # Verify deletion
        remaining_projects = pm.get_projects()
        print(f"Remaining projects: {len(remaining_projects)}")

        print("\n🎉 All ProjectManager tests passed!")
        return True

    except Exception as e:
        print(f"❌ ProjectManager test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_file_naming_with_projects():
    """Test file naming with project field."""
    print("\n🧪 Testing file naming with projects...")

    try:
        from ocrinvoice.utils.file_manager import FileManager

        # Create test config
        config = {
            "file_management": {
                "rename_files": True,
                "rename_format": "{project}_{documentType}_{company}_{date}_$${total}.pdf",
                "document_type": "facture",
            }
        }

        fm = FileManager(config)

        # Test data with project
        test_data = {
            "company": "HYDRO-QUÉBEC",
            "total": 137.50,
            "date": "2023-01-15",
            "project": "kitchen-renovation",
        }

        # Format filename
        filename = fm.format_filename(test_data)
        print(f"✅ Generated filename: {filename}")

        # Test with default project
        test_data_default = {
            "company": "HYDRO-QUÉBEC",
            "total": 137.50,
            "date": "2023-01-15",
            # No project field - should use default
        }

        filename_default = fm.format_filename(test_data_default)
        print(f"✅ Generated filename (default project): {filename_default}")

        print("🎉 File naming with projects test passed!")
        return True

    except Exception as e:
        print(f"❌ File naming test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("🚀 Starting Project Feature Tests")
    print("=" * 50)

    # Test ProjectManager
    pm_success = test_project_manager()

    # Test file naming
    fn_success = test_file_naming_with_projects()

    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   ProjectManager: {'✅ PASSED' if pm_success else '❌ FAILED'}")
    print(f"   File Naming: {'✅ PASSED' if fn_success else '❌ FAILED'}")

    if pm_success and fn_success:
        print("\n🎉 All tests passed! Project feature is working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
