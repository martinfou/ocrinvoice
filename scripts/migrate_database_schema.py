#!/usr/bin/env python3
"""
Migrate SQLite database schema from canonical_name to business_name.

This script updates the existing database schema to use the new format.
"""

import sqlite3
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def migrate_database_schema(db_path: str) -> bool:
    """Migrate the database schema from canonical_name to business_name."""
    try:
        print(f"🔄 Migrating database schema: {db_path}")
        
        # Create backup
        backup_path = db_path.replace('.db', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"💾 Created backup: {backup_path}")
        
        with sqlite3.connect(db_path) as conn:
            # Check if migration is needed
            cursor = conn.execute("PRAGMA table_info(businesses)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'business_name' in columns:
                print("✅ Database already has business_name column")
                return True
            
            if 'canonical_name' not in columns:
                print("❌ Database doesn't have canonical_name column")
                return False
            
            print("🔄 Renaming canonical_name column to business_name...")
            
            # Create new table with business_name
            conn.execute("""
                CREATE TABLE businesses_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    business_name TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT DEFAULT '{}'
                )
            """)
            
            # Copy data from old table to new table
            conn.execute("""
                INSERT INTO businesses_new (id, business_name, created_at, updated_at, metadata)
                SELECT id, canonical_name, created_at, updated_at, metadata
                FROM businesses
            """)
            
            # Drop old table and rename new table
            conn.execute("DROP TABLE businesses")
            conn.execute("ALTER TABLE businesses_new RENAME TO businesses")
            
            print("✅ Successfully migrated database schema")
            return True
            
    except Exception as e:
        print(f"❌ Error migrating database schema: {e}")
        return False

def main():
    """Main function."""
    config_dir = Path(__file__).parent.parent / "config"
    db_path = config_dir / "ocrinvoice.db"
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    success = migrate_database_schema(str(db_path))
    
    if success:
        print("✅ Database migration completed successfully!")
    else:
        print("❌ Database migration failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 