"""
Assets Manager Database - SQLite-based asset catalog and cache

Provides fast search and metadata caching for published assets.

Phase 1: Core database operations
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Debug flag
DEBUG = os.environ.get('MONO_DEBUG', '0').lower() in ('1', 'true', 'yes')

def debug_print(*args, **kwargs):
    """Print only if DEBUG mode is enabled"""
    if DEBUG:
        print(*args, **kwargs)


class AssetDatabase:
    """SQLite database for asset metadata and caching"""
    
    def __init__(self, db_path=None):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file. 
                    If None, uses default location: config/assets_manager/asset_cache.db
        """
        if db_path is None:
            # Default location relative to package root
            config_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config', 'assets_manager')
            os.makedirs(config_dir, exist_ok=True)
            db_path = os.path.join(config_dir, 'asset_cache.db')
        
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        debug_print(f"📊 Database path: {self.db_path}")
        
        # Connect and initialize
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Connect to database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Allow dict-like access
            self.cursor = self.conn.cursor()
            debug_print(f"✅ Connected to database: {self.db_path}")
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            raise
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        try:
            # Assets table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS assets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filepath TEXT UNIQUE NOT NULL,
                    filename TEXT NOT NULL,
                    asset_name TEXT NOT NULL,
                    asset_type TEXT,
                    department TEXT,
                    file_format TEXT,
                    file_size INTEGER,
                    created_date TEXT,
                    modified_date TEXT,
                    version TEXT,
                    thumbnail_path TEXT,
                    metadata_json TEXT,
                    tags TEXT,
                    description TEXT,
                    scan_date TEXT
                )
            """)
            
            # Recent assets table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS recent_assets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_id INTEGER,
                    access_time TEXT,
                    FOREIGN KEY(asset_id) REFERENCES assets(id)
                )
            """)
            
            # Create indexes for fast queries
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_asset_name ON assets(asset_name)
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_asset_type ON assets(asset_type)
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_file_format ON assets(file_format)
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_modified_date ON assets(modified_date)
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tags ON assets(tags)
            """)
            
            self.conn.commit()
            debug_print("✅ Database tables created/verified")
            
        except Exception as e:
            print(f"❌ Failed to create tables: {e}")
            raise
    
    def add_asset(self, asset_data: Dict) -> int:
        """
        Add or update asset in database
        
        Args:
            asset_data: Dictionary with asset information
            
        Returns:
            Asset ID
        """
        try:
            # Extract fields
            filepath = asset_data.get('filepath')
            filename = asset_data.get('filename', os.path.basename(filepath))
            asset_name = asset_data.get('asset_name', '')
            asset_type = asset_data.get('asset_type', '')
            department = asset_data.get('department', '')
            file_format = asset_data.get('file_format', '')
            file_size = asset_data.get('file_size', 0)
            created_date = asset_data.get('created_date', '')
            modified_date = asset_data.get('modified_date', '')
            version = asset_data.get('version', '')
            thumbnail_path = asset_data.get('thumbnail_path', '')
            metadata_json = json.dumps(asset_data.get('metadata', {}))
            tags = asset_data.get('tags', '')
            description = asset_data.get('description', '')
            scan_date = datetime.now().isoformat()
            
            # Insert or replace
            self.cursor.execute("""
                INSERT OR REPLACE INTO assets (
                    filepath, filename, asset_name, asset_type, department,
                    file_format, file_size, created_date, modified_date, version,
                    thumbnail_path, metadata_json, tags, description, scan_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                filepath, filename, asset_name, asset_type, department,
                file_format, file_size, created_date, modified_date, version,
                thumbnail_path, metadata_json, tags, description, scan_date
            ))
            
            self.conn.commit()
            asset_id = self.cursor.lastrowid
            debug_print(f"✅ Added asset: {filename} (ID: {asset_id})")
            return asset_id
            
        except Exception as e:
            print(f"❌ Failed to add asset: {e}")
            return -1
    
    def get_asset(self, asset_id: int) -> Optional[Dict]:
        """Get asset by ID"""
        try:
            self.cursor.execute("SELECT * FROM assets WHERE id = ?", (asset_id,))
            row = self.cursor.fetchone()
            if row:
                return dict(row)
            return None
        except Exception as e:
            print(f"❌ Failed to get asset: {e}")
            return None
    
    def get_asset_by_path(self, filepath: str) -> Optional[Dict]:
        """Get asset by filepath"""
        try:
            self.cursor.execute("SELECT * FROM assets WHERE filepath = ?", (filepath,))
            row = self.cursor.fetchone()
            if row:
                return dict(row)
            return None
        except Exception as e:
            print(f"❌ Failed to get asset by path: {e}")
            return None
    
    def search_assets(
        self,
        search_text: Optional[str] = None,
        asset_type: Optional[str] = None,
        file_format: Optional[str] = None,
        department: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """
        Search for assets with filters
        
        Args:
            search_text: Text to search in filename, asset_name, description
            asset_type: Filter by asset type (_characters, _props, etc.)
            file_format: Filter by file format (usd, fbx, abc, etc.)
            department: Filter by department
            tags: List of tags to filter by
            limit: Maximum number of results
            
        Returns:
            List of asset dictionaries
        """
        try:
            query = "SELECT * FROM assets WHERE 1=1"
            params = []
            
            # Text search
            if search_text:
                query += " AND (filename LIKE ? OR asset_name LIKE ? OR description LIKE ?)"
                search_pattern = f"%{search_text}%"
                params.extend([search_pattern, search_pattern, search_pattern])
            
            # Asset type filter
            if asset_type:
                query += " AND asset_type = ?"
                params.append(asset_type)
            
            # File format filter
            if file_format:
                query += " AND file_format = ?"
                params.append(file_format)
            
            # Department filter
            if department:
                query += " AND department = ?"
                params.append(department)
            
            # Tags filter (comma-separated)
            if tags:
                for tag in tags:
                    query += " AND tags LIKE ?"
                    params.append(f"%{tag}%")
            
            # Order by modified date (newest first)
            query += " ORDER BY modified_date DESC"
            
            # Limit results
            query += f" LIMIT {limit}"
            
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            
            results = [dict(row) for row in rows]
            debug_print(f"🔍 Search found {len(results)} assets")
            return results
            
        except Exception as e:
            print(f"❌ Failed to search assets: {e}")
            return []
    
    def get_all_asset_types(self) -> List[str]:
        """Get list of all unique asset types"""
        try:
            self.cursor.execute("SELECT DISTINCT asset_type FROM assets WHERE asset_type IS NOT NULL AND asset_type != ''")
            rows = self.cursor.fetchall()
            return [row[0] for row in rows]
        except Exception as e:
            print(f"❌ Failed to get asset types: {e}")
            return []
    
    def get_all_departments(self) -> List[str]:
        """Get list of all unique departments"""
        try:
            self.cursor.execute("SELECT DISTINCT department FROM assets WHERE department IS NOT NULL AND department != ''")
            rows = self.cursor.fetchall()
            return [row[0] for row in rows]
        except Exception as e:
            print(f"❌ Failed to get departments: {e}")
            return []
    
    def get_all_file_formats(self) -> List[str]:
        """Get list of all unique file formats"""
        try:
            self.cursor.execute("SELECT DISTINCT file_format FROM assets WHERE file_format IS NOT NULL AND file_format != ''")
            rows = self.cursor.fetchall()
            return [row[0] for row in rows]
        except Exception as e:
            print(f"❌ Failed to get file formats: {e}")
            return []
    
    def add_recent_asset(self, asset_id: int):
        """Add asset to recent access list"""
        try:
            access_time = datetime.now().isoformat()
            self.cursor.execute("""
                INSERT INTO recent_assets (asset_id, access_time)
                VALUES (?, ?)
            """, (asset_id, access_time))
            self.conn.commit()
            debug_print(f"✅ Added to recent: asset ID {asset_id}")
        except Exception as e:
            print(f"❌ Failed to add recent asset: {e}")
    
    def get_recent_assets(self, limit: int = 20) -> List[Dict]:
        """Get recently accessed assets"""
        try:
            self.cursor.execute("""
                SELECT a.* FROM assets a
                JOIN recent_assets r ON a.id = r.asset_id
                ORDER BY r.access_time DESC
                LIMIT ?
            """, (limit,))
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"❌ Failed to get recent assets: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            stats = {}
            
            # Total assets
            self.cursor.execute("SELECT COUNT(*) FROM assets")
            stats['total_assets'] = self.cursor.fetchone()[0]
            
            # Assets by type
            self.cursor.execute("""
                SELECT asset_type, COUNT(*) as count 
                FROM assets 
                WHERE asset_type IS NOT NULL AND asset_type != ''
                GROUP BY asset_type
            """)
            stats['by_type'] = {row[0]: row[1] for row in self.cursor.fetchall()}
            
            # Assets by format
            self.cursor.execute("""
                SELECT file_format, COUNT(*) as count 
                FROM assets 
                WHERE file_format IS NOT NULL AND file_format != ''
                GROUP BY file_format
            """)
            stats['by_format'] = {row[0]: row[1] for row in self.cursor.fetchall()}
            
            # Database file size
            if os.path.exists(self.db_path):
                stats['db_size_bytes'] = os.path.getsize(self.db_path)
                stats['db_size_mb'] = round(stats['db_size_bytes'] / (1024 * 1024), 2)
            
            return stats
            
        except Exception as e:
            print(f"❌ Failed to get stats: {e}")
            return {}
    
    def vacuum(self):
        """Optimize database (reclaim space, rebuild indexes)"""
        try:
            debug_print("🔧 Running VACUUM...")
            self.cursor.execute("VACUUM")
            self.conn.commit()
            debug_print("✅ Database optimized")
        except Exception as e:
            print(f"❌ Failed to vacuum database: {e}")
    
    def clear_all(self):
        """Clear all assets (use with caution!)"""
        try:
            self.cursor.execute("DELETE FROM recent_assets")
            self.cursor.execute("DELETE FROM assets")
            self.conn.commit()
            debug_print("✅ Database cleared")
        except Exception as e:
            print(f"❌ Failed to clear database: {e}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            debug_print("✅ Database connection closed")
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Convenience functions for common operations

def create_database(db_path=None) -> AssetDatabase:
    """Create and initialize a new database"""
    return AssetDatabase(db_path)

def get_default_database() -> AssetDatabase:
    """Get database with default location"""
    return AssetDatabase()




