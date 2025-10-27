"""
Assets Manager Metadata - Parse and manage asset metadata

Reads metadata from JSON files, USD files, or generates default metadata.

Phase 1: Basic JSON metadata parsing
"""

import os
import json
from typing import Dict, Optional, Tuple
from datetime import datetime

# Debug flag
DEBUG = os.environ.get('MONO_DEBUG', '0').lower() in ('1', 'true', 'yes')

def debug_print(*args, **kwargs):
    """Print only if DEBUG mode is enabled"""
    if DEBUG:
        print(*args, **kwargs)


class MetadataManager:
    """Manager for asset metadata"""
    
    def __init__(self):
        """Initialize metadata manager"""
        debug_print("📋 Metadata Manager initialized")
    
    def read_metadata(self, asset_path: str) -> Dict:
        """
        Read metadata for an asset
        
        Tries multiple sources in order:
        1. metadata.json in same folder
        2. USD metadata (if USD file)
        3. Generate default metadata
        
        Args:
            asset_path: Path to asset file
            
        Returns:
            Dictionary with metadata
        """
        try:
            # Try to read from metadata.json
            metadata_json = self._find_metadata_json(asset_path)
            if metadata_json:
                metadata = self.read_metadata_json(metadata_json)
                if metadata:
                    debug_print(f"✅ Loaded metadata from JSON: {os.path.basename(metadata_json)}")
                    return metadata
            
            # Try to read from USD (Phase 1: Skip, Phase 3: Implement)
            if asset_path.endswith(('.usd', '.usda', '.usdc')):
                # TODO Phase 3: Implement USD metadata extraction
                pass
            
            # Generate default metadata
            debug_print(f"📝 Generating default metadata for: {os.path.basename(asset_path)}")
            return self.generate_default_metadata(asset_path)
        
        except Exception as e:
            print(f"❌ Error reading metadata for {asset_path}: {e}")
            return self.generate_default_metadata(asset_path)
    
    def _find_metadata_json(self, asset_path: str) -> Optional[str]:
        """
        Find metadata.json file for asset
        
        Looks for:
        1. {asset_name}_metadata.json (e.g., char_hero_v003_metadata.json)
        2. metadata.json in same folder
        
        Args:
            asset_path: Path to asset file
            
        Returns:
            Path to metadata.json or None
        """
        try:
            asset_dir = os.path.dirname(asset_path)
            asset_filename = os.path.basename(asset_path)
            asset_name = os.path.splitext(asset_filename)[0]
            
            # Try specific metadata file
            specific_metadata = os.path.join(asset_dir, f"{asset_name}_metadata.json")
            if os.path.isfile(specific_metadata):
                return specific_metadata
            
            # Try generic metadata.json
            generic_metadata = os.path.join(asset_dir, "metadata.json")
            if os.path.isfile(generic_metadata):
                return generic_metadata
            
            return None
        
        except Exception as e:
            debug_print(f"⚠️ Error finding metadata.json: {e}")
            return None
    
    def read_metadata_json(self, json_path: str) -> Optional[Dict]:
        """
        Read metadata from JSON file
        
        Args:
            json_path: Path to metadata.json
            
        Returns:
            Dictionary with metadata or None if failed
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            debug_print(f"✅ Read metadata JSON: {os.path.basename(json_path)}")
            return metadata
        
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {json_path}: {e}")
            return None
        except Exception as e:
            print(f"❌ Error reading {json_path}: {e}")
            return None
    
    def write_metadata_json(self, json_path: str, metadata: Dict) -> bool:
        """
        Write metadata to JSON file
        
        Args:
            json_path: Path to save metadata.json
            metadata: Metadata dictionary
            
        Returns:
            True if successful
        """
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=4, ensure_ascii=False)
            
            debug_print(f"✅ Wrote metadata JSON: {os.path.basename(json_path)}")
            return True
        
        except Exception as e:
            print(f"❌ Error writing {json_path}: {e}")
            return False
    
    def generate_default_metadata(self, asset_path: str) -> Dict:
        """
        Generate default metadata for asset
        
        Args:
            asset_path: Path to asset file
            
        Returns:
            Dictionary with default metadata
        """
        try:
            filename = os.path.basename(asset_path)
            name_without_ext = os.path.splitext(filename)[0]
            
            # Get file stats
            stat = os.stat(asset_path)
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            
            metadata = {
                'asset_name': name_without_ext,
                'filename': filename,
                'version': '',  # Will be extracted by scanner
                'created_date': modified_time.isoformat(),
                'modified_date': modified_time.isoformat(),
                'created_by': '',
                'description': f'Auto-generated metadata for {filename}',
                'tags': [],
                'dependencies': [],
                'thumbnail': '',
                'custom': {}
            }
            
            return metadata
        
        except Exception as e:
            print(f"❌ Error generating default metadata: {e}")
            return {}
    
    def extract_usd_metadata(self, usd_path: str) -> Dict:
        """
        Extract metadata from USD file
        
        Phase 1: Not implemented
        Phase 3: Implement using pxr.Usd
        
        Args:
            usd_path: Path to USD file
            
        Returns:
            Dictionary with USD metadata
        """
        # TODO Phase 3: Implement USD metadata extraction
        # Will use pxr.Usd to read metadata from USD file
        debug_print(f"⚠️ USD metadata extraction not yet implemented (Phase 3)")
        return {}
    
    def merge_metadata(self, base: Dict, override: Dict) -> Dict:
        """
        Merge two metadata dictionaries
        
        Args:
            base: Base metadata
            override: Override metadata (takes precedence)
            
        Returns:
            Merged metadata
        """
        merged = base.copy()
        merged.update(override)
        return merged
    
    def validate_metadata(self, metadata: Dict) -> Tuple[bool, list]:
        """
        Validate metadata structure
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Required fields
        required_fields = ['asset_name', 'filename']
        for field in required_fields:
            if field not in metadata or not metadata[field]:
                errors.append(f"Missing required field: {field}")
        
        # Optional but recommended fields
        recommended_fields = ['version', 'description', 'created_date']
        for field in recommended_fields:
            if field not in metadata or not metadata[field]:
                debug_print(f"⚠️ Missing recommended field: {field}")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def create_metadata_template(self, asset_path: str) -> Dict:
        """
        Create a metadata template for an asset
        
        Args:
            asset_path: Path to asset file
            
        Returns:
            Dictionary with metadata template
        """
        filename = os.path.basename(asset_path)
        name_without_ext = os.path.splitext(filename)[0]
        
        template = {
            'asset_name': name_without_ext,
            'filename': filename,
            'version': 'v001',
            'created_date': datetime.now().isoformat(),
            'modified_date': datetime.now().isoformat(),
            'created_by': 'artist_name',
            'description': 'Description of the asset',
            'tags': ['tag1', 'tag2', 'tag3'],
            'dependencies': [],
            'thumbnail': f'{name_without_ext}_thumb.jpg',
            'polycount': 0,
            'bounds': [0, 0, 0],
            'custom': {
                'notes': 'Additional notes',
                'approval_status': 'pending',
                'reviewer': ''
            }
        }
        
        return template
    
    def get_metadata_summary(self, metadata: Dict) -> str:
        """
        Get a human-readable summary of metadata
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Summary string
        """
        lines = []
        lines.append(f"Asset: {metadata.get('asset_name', 'Unknown')}")
        lines.append(f"Version: {metadata.get('version', 'Unknown')}")
        lines.append(f"Description: {metadata.get('description', 'No description')}")
        
        tags = metadata.get('tags', [])
        if isinstance(tags, list):
            lines.append(f"Tags: {', '.join(tags)}")
        elif isinstance(tags, str):
            lines.append(f"Tags: {tags}")
        
        lines.append(f"Modified: {metadata.get('modified_date', 'Unknown')}")
        
        return '\n'.join(lines)


# Convenience functions

def read_metadata(asset_path: str) -> Dict:
    """Read metadata for an asset"""
    manager = MetadataManager()
    return manager.read_metadata(asset_path)

def write_metadata(json_path: str, metadata: Dict) -> bool:
    """Write metadata to JSON file"""
    manager = MetadataManager()
    return manager.write_metadata_json(json_path, metadata)

def create_template(asset_path: str) -> Dict:
    """Create metadata template for asset"""
    manager = MetadataManager()
    return manager.create_metadata_template(asset_path)




