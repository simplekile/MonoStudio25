"""
Assets Manager Scanner - Scan _publish/ folders for published assets

Finds and catalogs published assets in project structure.

Phase 1: Basic scanning with file format detection
"""

import os
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Debug flag
DEBUG = os.environ.get('MONO_DEBUG', '0').lower() in ('1', 'true', 'yes')

def debug_print(*args, **kwargs):
    """Print only if DEBUG mode is enabled"""
    if DEBUG:
        print(*args, **kwargs)


# Supported asset formats
ASSET_FORMATS = {
    'geometry': ['.fbx', '.obj', '.abc', '.usd', '.usda', '.usdc', '.bgeo', '.bgeo.sc'],
    'texture': ['.jpg', '.jpeg', '.png', '.tga', '.exr', '.tif', '.tiff', '.hdr', '.hdri'],
    'cache': ['.bgeo', '.bgeo.sc', '.vdb', '.abc', '.pc2'],
    'scene': ['.usd', '.usda', '.usdc'],
    'material': ['.mtlx', '.vop', '.hda'],
}

# Flatten to single list for easy checking
ALL_ASSET_FORMATS = set()
for formats in ASSET_FORMATS.values():
    ALL_ASSET_FORMATS.update(formats)

# Version regex pattern
VERSION_PATTERN = re.compile(r'_v(\d{3,4})(?:[_\.]|$)', re.IGNORECASE)

# Folders to ignore during scanning
IGNORE_FOLDERS = {
    'backup', 'Vers', 'old', '.git', '__pycache__', 
    '_thumbnail', 'thumbnails',  # Thumbnail cache
    '.houdini', '.tmp', 'temp'
}


class AssetScanner:
    """Scanner for published assets in _publish/ directories"""
    
    def __init__(self, project_path: str):
        """
        Initialize scanner
        
        Args:
            project_path: Root path of project to scan
        """
        self.project_path = os.path.normpath(project_path)
        self.assets_found = []
        self.scan_stats = {
            'total_files': 0,
            'total_assets': 0,
            'by_format': {},
            'by_type': {},
            'scan_time': 0
        }
        
        debug_print(f"📡 Scanner initialized for: {self.project_path}")
    
    def scan_project(self, incremental=False) -> List[Dict]:
        """
        Scan entire project for published assets
        
        Args:
            incremental: If True, only scan files modified since last scan
            
        Returns:
            List of asset dictionaries
        """
        debug_print(f"🔍 Starting{'incremental' if incremental else 'full'} scan...")
        start_time = datetime.now()
        
        self.assets_found = []
        
        # Scan 01_assets/ folder (if exists)
        assets_dir = os.path.join(self.project_path, '01_assets')
        if os.path.isdir(assets_dir):
            debug_print(f"📁 Scanning assets directory: {assets_dir}")
            self._scan_assets_directory(assets_dir)
        
        # Scan 02_shots/ folder (if exists)
        shots_dir = os.path.join(self.project_path, '02_shots')
        if os.path.isdir(shots_dir):
            debug_print(f"📁 Scanning shots directory: {shots_dir}")
            self._scan_shots_directory(shots_dir)
        
        # Update stats
        end_time = datetime.now()
        self.scan_stats['scan_time'] = (end_time - start_time).total_seconds()
        self.scan_stats['total_assets'] = len(self.assets_found)
        
        debug_print(f"✅ Scan complete: {self.scan_stats['total_assets']} assets found in {self.scan_stats['scan_time']:.2f}s")
        
        return self.assets_found
    
    def _scan_assets_directory(self, assets_dir: str):
        """
        Scan 01_assets/ directory structure
        
        Structure:
        01_assets/
        ├── _characters/
        │   ├── char_hero/
        │   │   ├── 01_modeling/
        │   │   │   └── _publish/
        │   │   │       ├── char_hero_v003.usd
        │   │   │       └── char_hero_v003.fbx
        """
        try:
            # Iterate through asset types (_characters, _props, etc.)
            for asset_type in os.listdir(assets_dir):
                asset_type_path = os.path.join(assets_dir, asset_type)
                
                if not os.path.isdir(asset_type_path):
                    continue
                
                if asset_type in IGNORE_FOLDERS:
                    continue
                
                # Only process folders starting with underscore (convention)
                if not asset_type.startswith('_'):
                    continue
                
                debug_print(f"  📂 Scanning asset type: {asset_type}")
                
                # Iterate through assets (char_hero, prop_chair, etc.)
                for asset_name in os.listdir(asset_type_path):
                    asset_name_path = os.path.join(asset_type_path, asset_name)
                    
                    if not os.path.isdir(asset_name_path):
                        continue
                    
                    if asset_name in IGNORE_FOLDERS:
                        continue
                    
                    # Iterate through departments (01_modeling, 02_rigging, etc.)
                    for department in os.listdir(asset_name_path):
                        department_path = os.path.join(asset_name_path, department)
                        
                        if not os.path.isdir(department_path):
                            continue
                        
                        if department in IGNORE_FOLDERS:
                            continue
                        
                        # Look for _publish/ folder
                        publish_path = os.path.join(department_path, '_publish')
                        if os.path.isdir(publish_path):
                            debug_print(f"    📦 Found _publish/: {asset_name}/{department}")
                            self._scan_publish_folder(
                                publish_path,
                                asset_type=asset_type,
                                asset_name=asset_name,
                                department=department
                            )
        
        except Exception as e:
            print(f"❌ Error scanning assets directory: {e}")
    
    def _scan_shots_directory(self, shots_dir: str):
        """
        Scan 02_shots/ directory structure
        
        Structure:
        02_shots/
        ├── 01_layout/
        │   └── _publish/
        ├── 02_animation/
        │   └── _publish/
        └── 03_lighting/
            └── _publish/
        """
        try:
            # Iterate through shot departments
            for department in os.listdir(shots_dir):
                department_path = os.path.join(shots_dir, department)
                
                if not os.path.isdir(department_path):
                    continue
                
                if department in IGNORE_FOLDERS:
                    continue
                
                debug_print(f"  📂 Scanning shot department: {department}")
                
                # Look for _publish/ folder
                publish_path = os.path.join(department_path, '_publish')
                if os.path.isdir(publish_path):
                    debug_print(f"    📦 Found _publish/: shots/{department}")
                    self._scan_publish_folder(
                        publish_path,
                        asset_type='Shots',
                        asset_name=None,  # Shots don't have asset names
                        department=department
                    )
        
        except Exception as e:
            print(f"❌ Error scanning shots directory: {e}")
    
    def _scan_publish_folder(
        self, 
        publish_path: str, 
        asset_type: str, 
        asset_name: Optional[str], 
        department: str
    ):
        """
        Scan _publish/ folder for asset files
        
        Args:
            publish_path: Path to _publish/ folder
            asset_type: Asset type (_characters, _props, Shots, etc.)
            asset_name: Asset name (char_hero, prop_chair, etc.) or None for shots
            department: Department name (01_modeling, 02_rigging, etc.)
        """
        try:
            for filename in os.listdir(publish_path):
                filepath = os.path.join(publish_path, filename)
                
                # Skip directories
                if os.path.isdir(filepath):
                    continue
                
                # Check if file format is supported
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext not in ALL_ASSET_FORMATS:
                    continue
                
                # Skip metadata files (will be parsed separately)
                if filename.endswith('.json') or filename.endswith('.xml'):
                    continue
                
                self.scan_stats['total_files'] += 1
                
                # Parse asset information
                asset_info = self._parse_asset_file(
                    filepath,
                    asset_type=asset_type,
                    asset_name=asset_name,
                    department=department
                )
                
                if asset_info:
                    self.assets_found.append(asset_info)
                    
                    # Update format stats
                    fmt = asset_info.get('file_format', 'unknown')
                    self.scan_stats['by_format'][fmt] = self.scan_stats['by_format'].get(fmt, 0) + 1
                    
                    # Update type stats
                    atype = asset_info.get('asset_type', 'unknown')
                    self.scan_stats['by_type'][atype] = self.scan_stats['by_type'].get(atype, 0) + 1
        
        except Exception as e:
            print(f"❌ Error scanning publish folder {publish_path}: {e}")
    
    def _parse_asset_file(
        self, 
        filepath: str, 
        asset_type: str, 
        asset_name: Optional[str], 
        department: str
    ) -> Optional[Dict]:
        """
        Parse asset file and extract metadata
        
        Args:
            filepath: Full path to asset file
            asset_type: Asset type
            asset_name: Asset name (or None for shots)
            department: Department name
            
        Returns:
            Dictionary with asset information
        """
        try:
            filename = os.path.basename(filepath)
            file_ext = os.path.splitext(filename)[1].lower()
            
            # Get file stats
            stat = os.stat(filepath)
            file_size = stat.st_size
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            created_time = datetime.fromtimestamp(stat.st_ctime)
            
            # Extract version
            version = self._extract_version(filename)
            
            # Determine file format category
            file_format = file_ext.lstrip('.')
            
            # Infer asset name if not provided (for shots)
            if asset_name is None:
                asset_name = self._infer_asset_name(filename)
            
            # Build asset dictionary
            asset_data = {
                'filepath': os.path.normpath(filepath),
                'filename': filename,
                'asset_name': asset_name,
                'asset_type': asset_type,
                'department': department,
                'file_format': file_format,
                'file_size': file_size,
                'created_date': created_time.isoformat(),
                'modified_date': modified_time.isoformat(),
                'version': version,
                'thumbnail_path': '',  # Will be generated later
                'metadata': {},  # Will be loaded from metadata.json if exists
                'tags': '',  # Will be loaded from metadata
                'description': '',  # Will be loaded from metadata
            }
            
            debug_print(f"      ✅ Found: {filename} ({file_format}, {version})")
            
            return asset_data
        
        except Exception as e:
            print(f"❌ Error parsing asset file {filepath}: {e}")
            return None
    
    def _extract_version(self, filename: str) -> str:
        """
        Extract version string from filename
        
        Examples:
            char_hero_v003.usd → v003
            prop_chair_v12.fbx → v12
            Sh010_v001.abc → v001
        
        Returns:
            Version string (e.g., "v003") or empty string if not found
        """
        match = VERSION_PATTERN.search(filename)
        if match:
            version_num = match.group(1)
            return f"v{version_num}"
        return ""
    
    def _infer_asset_name(self, filename: str) -> str:
        """
        Infer asset name from filename (for shots without explicit asset_name)
        
        Examples:
            Sh010_lighting_v001.usd → Sh010
            Sh020_animation_v002.abc → Sh020
        
        Returns:
            Inferred asset name or filename without extension
        """
        # Try to extract shot name (Sh010, SH020, etc.)
        shot_pattern = re.compile(r'^(Sh\d+|SH\d+)', re.IGNORECASE)
        match = shot_pattern.match(filename)
        if match:
            return match.group(1)
        
        # Fallback: use filename without version and extension
        name = os.path.splitext(filename)[0]
        # Remove version suffix
        name = VERSION_PATTERN.sub('', name).rstrip('_')
        return name
    
    def get_stats(self) -> Dict:
        """Get scan statistics"""
        return self.scan_stats.copy()
    
    def filter_by_type(self, asset_type: str) -> List[Dict]:
        """Filter assets by type"""
        return [a for a in self.assets_found if a.get('asset_type') == asset_type]
    
    def filter_by_format(self, file_format: str) -> List[Dict]:
        """Filter assets by file format"""
        return [a for a in self.assets_found if a.get('file_format') == file_format]
    
    def filter_by_name(self, search_text: str) -> List[Dict]:
        """Filter assets by name (fuzzy search)"""
        search_lower = search_text.lower()
        return [
            a for a in self.assets_found 
            if search_lower in a.get('filename', '').lower() 
            or search_lower in a.get('asset_name', '').lower()
        ]


# Convenience functions

def scan_project(project_path: str) -> List[Dict]:
    """Scan project and return list of assets"""
    scanner = AssetScanner(project_path)
    return scanner.scan_project()

def quick_scan(project_path: str, asset_type: Optional[str] = None) -> List[Dict]:
    """
    Quick scan with optional type filter
    
    Args:
        project_path: Project root path
        asset_type: Optional asset type filter
        
    Returns:
        List of assets
    """
    scanner = AssetScanner(project_path)
    assets = scanner.scan_project()
    
    if asset_type:
        assets = scanner.filter_by_type(asset_type)
    
    return assets




