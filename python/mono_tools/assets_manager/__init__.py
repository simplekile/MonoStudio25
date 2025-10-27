"""
Mono Assets Manager - Published Asset Browser for Houdini

Browse, preview, and import published assets (USD, FBX, ABC, etc.) from _publish/ directories.

Compatible with Houdini 21+ (PySide6)
Version: 1.0.0 (Phase 1 - Core Foundation)
"""

__version__ = "1.0.0"
__author__ = "MonoStudio"

# Core components (will be implemented in phases)
# Phase 1: Scanner, Database, Metadata
# Phase 2: Browser UI
# Phase 3: Thumbnails
# Phase 4: Import/Reference
# Phase 5: Advanced Features
# Phase 6: Integration

# Public API (Phase 1 - Basic scanning)
try:
    from .assets_manager_database import AssetDatabase
    from .assets_manager_scanner import AssetScanner
    from .assets_manager_metadata import MetadataManager
except ImportError as e:
    # During development, some modules may not exist yet
    print(f"⚠️ Assets Manager: Some modules not yet implemented: {e}")

# Thumbnail API (Phase 3)
try:
    from .assets_manager_thumbnails import ThumbnailGenerator, generate_thumbnail, get_thumbnail
except ImportError as e:
    debug_print(f"⚠️ Thumbnails not available: {e}")
    ThumbnailGenerator = None
    generate_thumbnail = None
    get_thumbnail = None

# Browser API (Phase 3)
try:
    from .assets_manager_browser import AssetGridView, create_grid_view
except ImportError as e:
    debug_print(f"⚠️ Browser widgets not available: {e}")
    AssetGridView = None
    create_grid_view = None

# UI API (Phase 2)
try:
    from .assets_manager import show_mono_assets_manager, MonoAssetsManager
except ImportError as e:
    # UI not available without PySide6
    def show_mono_assets_manager():
        """Show Assets Manager browser dialog (Phase 2)"""
        raise RuntimeError("Assets Manager UI requires PySide6")
    MonoAssetsManager = None

def import_asset(asset_path, mode="usd_reference", target=None):
    """Import asset into Houdini scene (Phase 4)"""
    raise NotImplementedError("Asset import not yet implemented (Phase 4)")

def reference_asset(asset_path, reference_type="usd_reference"):
    """Reference asset (non-destructive) (Phase 4)"""
    raise NotImplementedError("Asset reference not yet implemented (Phase 4)")

def search_assets(project_path, search_text=None, asset_type=None, file_format=None, **kwargs):
    """Search for assets in project (Phase 1 - Basic, Phase 5 - Advanced)"""
    # Basic implementation for Phase 1
    try:
        from .assets_manager_scanner import AssetScanner
        scanner = AssetScanner(project_path)
        assets = scanner.scan_project()
        
        # Basic filtering (Phase 1)
        if search_text:
            assets = [a for a in assets if search_text.lower() in a['filename'].lower()]
        if asset_type:
            assets = [a for a in assets if a.get('asset_type') == asset_type]
        if file_format:
            assets = [a for a in assets if a.get('file_format') == file_format]
        
        return assets
    except Exception as e:
        print(f"❌ Error searching assets: {e}")
        return []

# Version info
def get_version():
    """Get Assets Manager version"""
    return __version__

# Exports
__all__ = [
    # Core classes (Phase 1)
    'AssetDatabase',
    'AssetScanner',
    'MetadataManager',
    
    # UI classes & functions (Phase 2)
    'show_mono_assets_manager',
    'MonoAssetsManager',
    
    # Thumbnail classes & functions (Phase 3)
    'ThumbnailGenerator',
    'generate_thumbnail',
    'get_thumbnail',
    
    # Browser widgets (Phase 3)
    'AssetGridView',
    'create_grid_view',
    
    # Asset operations (Phase 4)
    'import_asset',
    'reference_asset',
    
    # Search & utilities (Phase 1+)
    'search_assets',
    'get_version',
]




