#!/usr/bin/env python3
"""
Migration script to transition from JSON-based storage to SQLite database.

This script will:
1. Create a new SQLite database
2. Migrate existing data from JSON files
3. Validate the migration
4. Create a backup of the original JSON files
"""

import sys
import os
import json
import shutil
from pathlib import Path
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ocrinvoice.business.database_manager import DatabaseManager


def backup_json_files(config_dir: Path) -> str:
    """Create a backup of existing JSON files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = config_dir / f"json_backup_{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    
    # Backup all JSON files
    json_files = [
        "business_mappings.json",
        "business_mappings_v2.json", 
        "projects.json",
        "categories.json"
    ]
    
    for json_file in json_files:
        source_file = config_dir / json_file
        if source_file.exists():
            shutil.copy2(source_file, backup_dir / json_file)
            print(f"✅ Backed up {json_file}")
    
    return str(backup_dir)


def migrate_data(config_dir: Path) -> bool:
    """Migrate data from JSON files to SQLite database."""
    print("🔄 Starting migration to SQLite database...")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Migrate business mappings
    business_files = [
        config_dir / "business_mappings_v2.json",
        config_dir / "business_mappings.json"
    ]
    
    for business_file in business_files:
        if business_file.exists():
            print(f"📊 Migrating business data from {business_file.name}...")
            if db_manager.migrate_from_json(str(business_file)):
                print(f"✅ Successfully migrated {business_file.name}")
            else:
                print(f"❌ Failed to migrate {business_file.name}")
                return False
    
    # Migrate projects (if they exist)
    projects_file = config_dir / "projects.json"
    if projects_file.exists():
        print("📋 Migrating projects...")
        try:
            with open(projects_file, 'r', encoding='utf-8') as f:
                projects_data = json.load(f)
            
            for project in projects_data:
                name = project.get('name', '')
                description = project.get('description', '')
                if name:
                    project_id = db_manager.add_project(name, description)
                    if project_id:
                        print(f"  ✅ Added project: {name}")
                    else:
                        print(f"  ⚠️  Project already exists: {name}")
        except Exception as e:
            print(f"❌ Error migrating projects: {e}")
    
    # Migrate categories (if they exist)
    categories_file = config_dir / "categories.json"
    if categories_file.exists():
        print("🏷️  Migrating categories...")
        try:
            with open(categories_file, 'r', encoding='utf-8') as f:
                categories_data = json.load(f)
            
            for category in categories_data:
                name = category.get('name', '')
                description = category.get('description', '')
                cra_code = category.get('cra_code', '')
                if name:
                    category_id = db_manager.add_category(name, description, cra_code)
                    if category_id:
                        print(f"  ✅ Added category: {name}")
                    else:
                        print(f"  ⚠️  Category already exists: {name}")
        except Exception as e:
            print(f"❌ Error migrating categories: {e}")
    
    return True


def validate_migration(db_manager: DatabaseManager, config_dir: Path) -> bool:
    """Validate the migration by comparing data counts."""
    print("🔍 Validating migration...")
    
    # Get database stats
    db_stats = db_manager.get_stats()
    
    # Count businesses in JSON files
    json_business_count = 0
    business_files = [
        config_dir / "business_mappings_v2.json",
        config_dir / "business_mappings.json"
    ]
    
    for business_file in business_files:
        if business_file.exists():
            try:
                with open(business_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    businesses = data.get('businesses', [])
                    json_business_count += len(businesses)
            except Exception as e:
                print(f"⚠️  Could not read {business_file.name}: {e}")
    
    # Count projects in JSON
    json_project_count = 0
    projects_file = config_dir / "projects.json"
    if projects_file.exists():
        try:
            with open(projects_file, 'r', encoding='utf-8') as f:
                projects_data = json.load(f)
                json_project_count = len(projects_data)
        except Exception as e:
            print(f"⚠️  Could not read projects.json: {e}")
    
    # Count categories in JSON
    json_category_count = 0
    categories_file = config_dir / "categories.json"
    if categories_file.exists():
        try:
            with open(categories_file, 'r', encoding='utf-8') as f:
                categories_data = json.load(f)
                json_category_count = len(categories_data)
        except Exception as e:
            print(f"⚠️  Could not read categories.json: {e}")
    
    # Compare counts
    print(f"📊 Migration Results:")
    print(f"  Businesses: JSON={json_business_count}, SQLite={db_stats['businesses']}")
    print(f"  Projects: JSON={json_project_count}, SQLite={db_stats['projects']}")
    print(f"  Categories: JSON={json_category_count}, SQLite={db_stats['categories']}")
    print(f"  Total Aliases: SQLite={db_stats['aliases']}")
    
    # Check if migration was successful
    if db_stats['businesses'] >= json_business_count:
        print("✅ Business migration successful!")
    else:
        print("❌ Business migration incomplete!")
        return False
    
    if db_stats['projects'] >= json_project_count:
        print("✅ Project migration successful!")
    else:
        print("❌ Project migration incomplete!")
        return False
    
    if db_stats['categories'] >= json_category_count:
        print("✅ Category migration successful!")
    else:
        print("❌ Category migration incomplete!")
        return False
    
    return True


def main():
    """Main migration function."""
    print("🚀 OCR Invoice Parser - JSON to SQLite Migration")
    print("=" * 50)
    
    # Get config directory
    config_dir = Path(__file__).parent.parent / "config"
    if not config_dir.exists():
        print(f"❌ Config directory not found: {config_dir}")
        return False
    
    print(f"📁 Config directory: {config_dir}")
    
    # Check if SQLite database already exists
    db_file = config_dir / "ocrinvoice.db"
    if db_file.exists():
        response = input(f"⚠️  SQLite database already exists at {db_file}. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("❌ Migration cancelled.")
            return False
        else:
            # Backup existing database
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = config_dir / "backups"
            backup_dir.mkdir(exist_ok=True)  # Ensure backup directory exists
            backup_db = backup_dir / f"ocrinvoice_backup_{timestamp}.db"
            shutil.copy2(db_file, backup_db)
            print(f"✅ Backed up existing database to {backup_db}")
    
    # Create backup of JSON files
    print("\n📦 Creating backup of JSON files...")
    backup_dir = backup_json_files(config_dir)
    print(f"✅ JSON files backed up to: {backup_dir}")
    
    # Migrate data
    print("\n🔄 Migrating data to SQLite...")
    if not migrate_data(config_dir):
        print("❌ Migration failed!")
        return False
    
    # Validate migration
    print("\n🔍 Validating migration...")
    db_manager = DatabaseManager()
    if not validate_migration(db_manager, config_dir):
        print("❌ Migration validation failed!")
        return False
    
    # Create final database backup
    print("\n💾 Creating database backup...")
    backup_path = db_manager.backup_database()
    print(f"✅ Database backed up to: {backup_path}")
    
    print("\n🎉 Migration completed successfully!")
    print("\n📋 Next steps:")
    print("1. Test the application with the new SQLite database")
    print("2. Update the application to use DatabaseManager instead of JSON files")
    print("3. Once confirmed working, you can remove the old JSON files")
    print(f"4. JSON backup is available at: {backup_dir}")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 