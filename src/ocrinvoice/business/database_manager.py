"""
Database Manager for OCR Invoice Parser

SQLite-based database manager for storing and managing:
- Business canonical names and aliases
- Projects
- Categories
- Invoice metadata
"""

import sqlite3
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    SQLite database manager for OCR Invoice Parser.
    
    Provides a clean, consistent interface for managing business data,
    projects, categories, and invoice metadata.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to SQLite database file. If None, uses default.
        """
        self.db_path = self._resolve_db_path(db_path)
        self._init_database()
    
    def _resolve_db_path(self, db_path: Optional[str]) -> str:
        """Resolve the database file path."""
        if db_path is None:
            config_dir = Path(__file__).parent.parent.parent.parent / "config"
            config_dir.mkdir(exist_ok=True)
            return str(config_dir / "ocrinvoice.db")
        return db_path
    
    def _init_database(self) -> None:
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Create businesses table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS businesses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    business_name TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT DEFAULT '{}'
                )
            """)
            
            # Create business_aliases table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS business_aliases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    business_id INTEGER NOT NULL,
                    keyword TEXT NOT NULL,
                    match_type TEXT NOT NULL DEFAULT 'exact',
                    case_sensitive BOOLEAN DEFAULT FALSE,
                    fuzzy_matching BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (business_id) REFERENCES businesses (id) ON DELETE CASCADE,
                    UNIQUE(business_id, keyword, match_type)
                )
            """)
            
            # Create business_indicators table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS business_indicators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    business_id INTEGER NOT NULL,
                    indicator TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (business_id) REFERENCES businesses (id) ON DELETE CASCADE,
                    UNIQUE(business_id, indicator)
                )
            """)
            
            # Create projects table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create categories table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    cra_code TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create invoice_metadata table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS invoice_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    project_id INTEGER,
                    category_id INTEGER,
                    extracted_data TEXT,  -- JSON string
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE SET NULL,
                    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_business_aliases_keyword ON business_aliases(keyword)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_business_aliases_match_type ON business_aliases(match_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_invoice_metadata_file_path ON invoice_metadata(file_path)")
            
            conn.commit()
    
    # Business Management Methods
    
    def add_business(self, business_name: str, metadata: Optional[Dict] = None) -> int:
        """
        Add a new business.
        
        Args:
            business_name: The business name
            metadata: Optional metadata dictionary
            
        Returns:
            Business ID if successful, None if already exists
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "INSERT INTO businesses (business_name, metadata) VALUES (?, ?)",
                    (business_name, json.dumps(metadata or {}))
                )
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Business '{business_name}' already exists")
            return None
    
    def get_business(self, business_id: int) -> Optional[Dict]:
        """Get business by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM businesses WHERE id = ?",
                (business_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def get_business_by_name(self, business_name: str) -> Optional[Dict]:
        """Get business by business name."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM businesses WHERE business_name = ?",
                (business_name,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def get_all_businesses(self) -> List[Dict]:
        """Get all businesses."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM businesses ORDER BY business_name")
            return [dict(row) for row in cursor.fetchall()]
    
    def update_business(self, business_id: int, business_name: str, metadata: Optional[Dict] = None) -> bool:
        """Update business name."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE businesses SET business_name = ?, metadata = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (business_name, json.dumps(metadata or {}), business_id)
                )
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"Business name '{business_name}' already exists")
            return False
    
    def delete_business(self, business_id: int) -> bool:
        """Delete business and all related data."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM businesses WHERE id = ?", (business_id,))
            return cursor.rowcount > 0
    
    # Business Alias Management
    
    def add_business_alias(self, business_id: int, keyword: str, match_type: str = "exact", 
                          case_sensitive: bool = False, fuzzy_matching: bool = True) -> bool:
        """Add a business alias/keyword."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT INTO business_aliases 
                       (business_id, keyword, match_type, case_sensitive, fuzzy_matching) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (business_id, keyword, match_type, case_sensitive, fuzzy_matching)
                )
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"Alias '{keyword}' already exists for business {business_id}")
            return False
    
    def get_business_aliases(self, business_id: int) -> List[Dict]:
        """Get all aliases for a business."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM business_aliases WHERE business_id = ? ORDER BY keyword",
                (business_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def find_business_by_keyword(self, keyword: str, match_type: Optional[str] = None) -> Optional[Dict]:
        """Find business by keyword/alias."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if match_type:
                cursor = conn.execute(
                    """SELECT b.* FROM businesses b 
                       JOIN business_aliases ba ON b.id = ba.business_id 
                       WHERE ba.keyword = ? AND ba.match_type = ?""",
                    (keyword, match_type)
                )
            else:
                cursor = conn.execute(
                    """SELECT b.* FROM businesses b 
                       JOIN business_aliases ba ON b.id = ba.business_id 
                       WHERE ba.keyword = ?""",
                    (keyword,)
                )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    # Project Management
    
    def add_project(self, name: str, description: Optional[str] = None) -> int:
        """Add a new project."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "INSERT INTO projects (name, description) VALUES (?, ?)",
                    (name, description)
                )
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Project '{name}' already exists")
            return None
    
    def get_all_projects(self) -> List[Dict]:
        """Get all projects."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM projects ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_project(self, project_id: int) -> Optional[Dict]:
        """Get project by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def update_project(self, project_id: int, name: str, description: Optional[str] = None) -> bool:
        """Update project."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE projects SET name = ?, description = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (name, description, project_id)
                )
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"Project name '{name}' already exists")
            return False
    
    def delete_project(self, project_id: int) -> bool:
        """Delete project."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            return cursor.rowcount > 0
    
    # Category Management
    
    def add_category(self, name: str, description: Optional[str] = None, cra_code: Optional[str] = None) -> int:
        """Add a new category."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "INSERT INTO categories (name, description, cra_code) VALUES (?, ?, ?)",
                    (name, description, cra_code)
                )
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Category '{name}' already exists")
            return None
    
    def get_all_categories(self) -> List[Dict]:
        """Get all categories."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM categories ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_category(self, category_id: int) -> Optional[Dict]:
        """Get category by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def update_category(self, category_id: int, name: str, description: Optional[str] = None, 
                       cra_code: Optional[str] = None) -> bool:
        """Update category."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE categories SET name = ?, description = ?, cra_code = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (name, description, cra_code, category_id)
                )
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"Category name '{name}' already exists")
            return False
    
    def delete_category(self, category_id: int) -> bool:
        """Delete category."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            return cursor.rowcount > 0
    
    # Invoice Metadata Management
    
    def save_invoice_metadata(self, file_path: str, extracted_data: Dict, 
                             project_id: Optional[int] = None, category_id: Optional[int] = None) -> bool:
        """Save invoice metadata."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT OR REPLACE INTO invoice_metadata 
                       (file_path, project_id, category_id, extracted_data) 
                       VALUES (?, ?, ?, ?)""",
                    (file_path, project_id, category_id, json.dumps(extracted_data))
                )
                return True
        except Exception as e:
            logger.error(f"Error saving invoice metadata: {e}")
            return False
    
    def get_invoice_metadata(self, file_path: str) -> Optional[Dict]:
        """Get invoice metadata by file path."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM invoice_metadata WHERE file_path = ?",
                (file_path,)
            )
            row = cursor.fetchone()
            if row:
                data = dict(row)
                if data.get('extracted_data'):
                    data['extracted_data'] = json.loads(data['extracted_data'])
                return data
            return None
    
    # Statistics and Reporting
    
    def get_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # Count businesses
            cursor = conn.execute("SELECT COUNT(*) FROM businesses")
            stats['businesses'] = cursor.fetchone()[0]
            
            # Count aliases
            cursor = conn.execute("SELECT COUNT(*) FROM business_aliases")
            stats['aliases'] = cursor.fetchone()[0]
            
            # Count projects
            cursor = conn.execute("SELECT COUNT(*) FROM projects")
            stats['projects'] = cursor.fetchone()[0]
            
            # Count categories
            cursor = conn.execute("SELECT COUNT(*) FROM categories")
            stats['categories'] = cursor.fetchone()[0]
            
            # Count invoices
            cursor = conn.execute("SELECT COUNT(*) FROM invoice_metadata")
            stats['invoices'] = cursor.fetchone()[0]
            
            return stats
    
    # Migration from JSON
    
    def migrate_from_json(self, json_file_path: str) -> bool:
        """Migrate data from JSON format to SQLite."""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with sqlite3.connect(self.db_path) as conn:
                # Migrate businesses
                if 'businesses' in data:
                    for business in data['businesses']:
                        business_name = business.get('business_name') or business.get('canonical_name', '')
                        if business_name:
                            business_id = self.add_business(business_name, business.get('metadata', {}))
                            if business_id:
                                # Migrate keywords
                                keywords = business.get('keywords', business.get('aliases', []))
                                for keyword in keywords:
                                    keyword_text = keyword.get('keyword', '')
                                    if keyword_text:
                                        self.add_business_alias(
                                            business_id,
                                            keyword_text,
                                            keyword.get('match_type', 'exact'),
                                            keyword.get('case_sensitive', False),
                                            keyword.get('fuzzy_matching', True)
                                        )
                
                # Migrate projects (if they exist in JSON)
                if 'projects' in data:
                    for project in data['projects']:
                        self.add_project(project.get('name', ''), project.get('description'))
                
                # Migrate categories (if they exist in JSON)
                if 'categories' in data:
                    for category in data['categories']:
                        self.add_category(
                            category.get('name', ''),
                            category.get('description'),
                            category.get('cra_code')
                        )
            
            logger.info(f"Successfully migrated data from {json_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error migrating from JSON: {e}")
            return False
    
    def backup_database(self, backup_path: Optional[str] = None, auto_cleanup: bool = True) -> str:
        """Create a backup of the database."""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Create backup in the backups folder
            backup_dir = Path(self.db_path).parent / "backups"
            backup_dir.mkdir(exist_ok=True)  # Ensure backup directory exists
            backup_path = str(backup_dir / f"ocrinvoice_backup_{timestamp}.db")
        
        import shutil
        shutil.copy2(self.db_path, backup_path)
        logger.info(f"Database backed up to {backup_path}")
        
        # Auto-cleanup old backups if enabled
        if auto_cleanup:
            self.cleanup_old_backups(keep_count=10)
        
        return backup_path
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Clean up old database backup files, keeping only the most recent ones.
        
        Args:
            keep_count: Number of recent backups to keep (default: 10)
            
        Returns:
            Number of backup files deleted
        """
        try:
            import os
            import glob
            
            # Get the backup directory
            backup_dir = Path(self.db_path).parent / "backups"
            if not backup_dir.exists():
                return 0  # No backup directory, nothing to clean
            
            # Find all database backup files
            backup_pattern = str(backup_dir / "ocrinvoice_backup_*.db")
            backup_files = glob.glob(backup_pattern)
            
            if len(backup_files) <= keep_count:
                return 0  # No cleanup needed
            
            # Sort by modification time (oldest first)
            backup_files.sort(key=lambda x: os.path.getmtime(x))
            
            # Delete oldest files, keeping the most recent ones
            files_to_delete = backup_files[:-keep_count]
            deleted_count = 0
            
            for backup_file in files_to_delete:
                try:
                    os.remove(backup_file)
                    deleted_count += 1
                    logger.info(f"🗑️ Deleted old database backup: {os.path.basename(backup_file)}")
                except Exception as e:
                    logger.warning(f"Could not delete backup {backup_file}: {e}")
            
            if deleted_count > 0:
                logger.info(f"✅ Cleaned up {deleted_count} old database backup files, keeping {keep_count} recent ones")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Could not cleanup old database backups: {e}")
            return 0 