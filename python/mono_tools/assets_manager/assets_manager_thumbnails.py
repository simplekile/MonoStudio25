"""
Assets Manager Thumbnails - Thumbnail generation and caching

Generate thumbnails for various asset types (USD, FBX, textures, etc.)

Phase 3: Thumbnail generation with caching
"""

import os
import hashlib
from typing import Optional, Tuple
from datetime import datetime, timedelta

# Import Qt for image handling
try:
    from ..qt import QtCore, QtGui, QtWidgets
except (ImportError, ValueError):
    try:
        from mono_tools.qt import QtCore, QtGui, QtWidgets
    except ImportError:
        from PySide6 import QtCore, QtGui, QtWidgets

# Debug flag
DEBUG = os.environ.get('MONO_DEBUG', '0').lower() in ('1', 'true', 'yes')

def debug_print(*args, **kwargs):
    """Print only if DEBUG mode is enabled"""
    if DEBUG:
        print(*args, **kwargs)


class ThumbnailGenerator:
    """
    Generate thumbnails for assets
    
    Supports:
    - Textures (direct image resize)
    - USD/FBX/ABC (placeholder for now, Houdini rendering in future)
    - Format icons (fallback)
    """
    
    def __init__(self, cache_dir=None, size=256):
        """
        Initialize thumbnail generator
        
        Args:
            cache_dir: Directory to cache thumbnails (default: config/assets_manager/thumbnails/)
            size: Thumbnail size in pixels (default: 256)
        """
        if cache_dir is None:
            # Default cache location
            config_dir = os.path.join(
                os.path.dirname(__file__), '..', '..', '..', 
                'config', 'assets_manager', 'thumbnails'
            )
            cache_dir = os.path.normpath(config_dir)
        
        self.cache_dir = cache_dir
        self.size = size
        self.memory_cache = {}  # In-memory cache (LRU)
        self.max_memory_items = 100
        
        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Cache TTL (7 days)
        self.cache_ttl = timedelta(days=7)
        
        debug_print(f"🖼️ ThumbnailGenerator initialized")
        debug_print(f"   Cache dir: {self.cache_dir}")
        debug_print(f"   Size: {self.size}x{self.size}")
    
    def get_thumbnail(self, asset_path: str, asset_format: str = None) -> QtGui.QPixmap:
        """
        Get thumbnail for asset (from cache or generate)
        
        Args:
            asset_path: Path to asset file
            asset_format: File format (usd, fbx, png, etc.)
            
        Returns:
            QPixmap with thumbnail
        """
        try:
            # Detect format if not provided
            if asset_format is None:
                asset_format = os.path.splitext(asset_path)[1].lstrip('.').lower()
            
            # Check memory cache first
            cache_key = self._get_cache_key(asset_path, self.size)
            if cache_key in self.memory_cache:
                debug_print(f"💾 Memory cache hit: {os.path.basename(asset_path)}")
                return self.memory_cache[cache_key]
            
            # Check disk cache
            cache_path = self._get_cache_path(asset_path, self.size)
            if self._is_cache_valid(cache_path, asset_path):
                debug_print(f"💿 Disk cache hit: {os.path.basename(asset_path)}")
                pixmap = QtGui.QPixmap(cache_path)
                if not pixmap.isNull():
                    self._add_to_memory_cache(cache_key, pixmap)
                    return pixmap
            
            # Generate new thumbnail
            debug_print(f"🔨 Generating thumbnail: {os.path.basename(asset_path)}")
            pixmap = self._generate_thumbnail(asset_path, asset_format)
            
            # Save to cache
            if pixmap and not pixmap.isNull():
                pixmap.save(cache_path, 'JPG', 90)
                self._add_to_memory_cache(cache_key, pixmap)
            
            return pixmap
            
        except Exception as e:
            debug_print(f"❌ Error getting thumbnail: {e}")
            return self._get_default_icon(asset_format)
    
    def _generate_thumbnail(self, asset_path: str, asset_format: str) -> QtGui.QPixmap:
        """
        Generate thumbnail based on asset type
        
        Args:
            asset_path: Path to asset file
            asset_format: File format
            
        Returns:
            QPixmap with thumbnail
        """
        try:
            # Texture files - direct image resize
            if asset_format in ['jpg', 'jpeg', 'png', 'tga', 'exr', 'tif', 'tiff', 'hdr']:
                return self._generate_image_thumbnail(asset_path)
            
            # Geometry files - placeholder for now
            elif asset_format in ['usd', 'usda', 'usdc', 'fbx', 'obj', 'abc', 'bgeo']:
                # Phase 3: Use format icon
                # Future Phase: Render geometry in Houdini
                return self._generate_geometry_placeholder(asset_format)
            
            # VDB volumes
            elif asset_format == 'vdb':
                return self._generate_vdb_placeholder()
            
            # Unknown format - generic icon
            else:
                return self._get_default_icon(asset_format)
                
        except Exception as e:
            debug_print(f"❌ Error generating thumbnail: {e}")
            return self._get_default_icon(asset_format)
    
    def _generate_image_thumbnail(self, image_path: str) -> QtGui.QPixmap:
        """
        Generate thumbnail from image file
        
        Args:
            image_path: Path to image file
            
        Returns:
            QPixmap with resized image
        """
        try:
            # Load image
            pixmap = QtGui.QPixmap(image_path)
            
            if pixmap.isNull():
                debug_print(f"⚠️ Failed to load image: {image_path}")
                return self._get_default_icon('image')
            
            # Scale to thumbnail size (maintain aspect ratio)
            scaled = pixmap.scaled(
                self.size, self.size,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            
            debug_print(f"✅ Image thumbnail: {os.path.basename(image_path)} ({pixmap.width()}x{pixmap.height()} → {scaled.width()}x{scaled.height()})")
            
            return scaled
            
        except Exception as e:
            debug_print(f"❌ Error generating image thumbnail: {e}")
            return self._get_default_icon('image')
    
    def _generate_geometry_placeholder(self, asset_format: str) -> QtGui.QPixmap:
        """
        Generate placeholder for geometry files
        
        Phase 3: Use format icon with gradient
        Future: Render actual geometry
        
        Args:
            asset_format: File format (usd, fbx, abc, etc.)
            
        Returns:
            QPixmap with placeholder
        """
        # Create colored placeholder based on format
        pixmap = QtGui.QPixmap(self.size, self.size)
        
        # Colors by format
        colors = {
            'usd': '#4a90d9',    # Blue
            'fbx': '#d97d4a',    # Orange
            'abc': '#4ad990',    # Green
            'obj': '#d94a90',    # Pink
            'bgeo': '#90d94a',   # Light green
        }
        
        color = colors.get(asset_format, '#888888')
        
        pixmap.fill(QtGui.QColor(color))
        
        # Draw format text
        painter = QtGui.QPainter(pixmap)
        painter.setPen(QtGui.QColor('#ffffff'))
        
        # Format label
        font = painter.font()
        font.setPixelSize(48)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(
            pixmap.rect(),
            QtCore.Qt.AlignCenter,
            asset_format.upper()
        )
        
        # Icon (simple cube)
        painter.setPen(QtGui.QPen(QtGui.QColor('#ffffff'), 3))
        painter.setBrush(QtCore.Qt.NoBrush)
        
        # Draw simple wireframe cube
        center_x = self.size / 2
        center_y = self.size / 2
        cube_size = self.size / 3
        
        # Front face
        painter.drawRect(
            int(center_x - cube_size/2), 
            int(center_y - cube_size/2),
            int(cube_size), 
            int(cube_size)
        )
        
        # Back face (offset)
        offset = cube_size / 4
        painter.drawRect(
            int(center_x - cube_size/2 - offset), 
            int(center_y - cube_size/2 - offset),
            int(cube_size), 
            int(cube_size)
        )
        
        # Connect corners
        painter.drawLine(
            int(center_x - cube_size/2), int(center_y - cube_size/2),
            int(center_x - cube_size/2 - offset), int(center_y - cube_size/2 - offset)
        )
        painter.drawLine(
            int(center_x + cube_size/2), int(center_y - cube_size/2),
            int(center_x + cube_size/2 - offset), int(center_y - cube_size/2 - offset)
        )
        
        painter.end()
        
        return pixmap
    
    def _generate_vdb_placeholder(self) -> QtGui.QPixmap:
        """Generate placeholder for VDB volumes"""
        pixmap = QtGui.QPixmap(self.size, self.size)
        pixmap.fill(QtGui.QColor('#6b4ad9'))  # Purple for volumes
        
        painter = QtGui.QPainter(pixmap)
        painter.setPen(QtGui.QColor('#ffffff'))
        
        # VDB label
        font = painter.font()
        font.setPixelSize(48)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(
            pixmap.rect(),
            QtCore.Qt.AlignCenter,
            'VDB'
        )
        
        painter.end()
        return pixmap
    
    def _get_default_icon(self, asset_format: str = None) -> QtGui.QPixmap:
        """
        Get default icon for unknown formats
        
        Args:
            asset_format: File format
            
        Returns:
            QPixmap with generic icon
        """
        pixmap = QtGui.QPixmap(self.size, self.size)
        pixmap.fill(QtGui.QColor('#3a3a3a'))
        
        painter = QtGui.QPainter(pixmap)
        painter.setPen(QtGui.QColor('#999999'))
        
        # Draw file icon
        font = painter.font()
        font.setPixelSize(32)
        painter.setFont(font)
        
        text = asset_format.upper() if asset_format else 'FILE'
        painter.drawText(
            pixmap.rect(),
            QtCore.Qt.AlignCenter,
            text
        )
        
        painter.end()
        return pixmap
    
    def _get_cache_key(self, asset_path: str, size: int) -> str:
        """Get cache key for asset"""
        # Use hash of path + size
        key_str = f"{asset_path}_{size}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cache_path(self, asset_path: str, size: int) -> str:
        """Get cache file path for asset"""
        cache_key = self._get_cache_key(asset_path, size)
        return os.path.join(self.cache_dir, f"{cache_key}.jpg")
    
    def _is_cache_valid(self, cache_path: str, asset_path: str) -> bool:
        """
        Check if cached thumbnail is still valid
        
        Args:
            cache_path: Path to cached thumbnail
            asset_path: Path to original asset
            
        Returns:
            True if cache is valid
        """
        try:
            # Check if cache exists
            if not os.path.exists(cache_path):
                return False
            
            # Check if asset exists
            if not os.path.exists(asset_path):
                return False
            
            # Check cache age (TTL)
            cache_mtime = datetime.fromtimestamp(os.path.getmtime(cache_path))
            cache_age = datetime.now() - cache_mtime
            if cache_age > self.cache_ttl:
                debug_print(f"⏰ Cache expired: {os.path.basename(cache_path)}")
                return False
            
            # Check if asset was modified after cache
            asset_mtime = datetime.fromtimestamp(os.path.getmtime(asset_path))
            if asset_mtime > cache_mtime:
                debug_print(f"🔄 Asset modified: {os.path.basename(asset_path)}")
                return False
            
            return True
            
        except Exception as e:
            debug_print(f"⚠️ Cache validation error: {e}")
            return False
    
    def _add_to_memory_cache(self, cache_key: str, pixmap: QtGui.QPixmap):
        """Add pixmap to memory cache (with LRU eviction)"""
        self.memory_cache[cache_key] = pixmap
        
        # LRU eviction if cache too large
        if len(self.memory_cache) > self.max_memory_items:
            # Remove oldest item (first inserted)
            oldest_key = next(iter(self.memory_cache))
            del self.memory_cache[oldest_key]
            debug_print(f"🗑️ LRU evicted: {oldest_key}")
    
    def clear_cache(self):
        """Clear all cached thumbnails"""
        try:
            # Clear memory cache
            self.memory_cache.clear()
            
            # Clear disk cache
            if os.path.exists(self.cache_dir):
                import shutil
                shutil.rmtree(self.cache_dir)
                os.makedirs(self.cache_dir, exist_ok=True)
            
            debug_print("✅ Cache cleared")
            
        except Exception as e:
            debug_print(f"❌ Error clearing cache: {e}")
    
    def get_cache_size(self) -> Tuple[int, int]:
        """
        Get cache size
        
        Returns:
            Tuple of (file_count, size_in_bytes)
        """
        try:
            if not os.path.exists(self.cache_dir):
                return (0, 0)
            
            file_count = 0
            total_size = 0
            
            for filename in os.listdir(self.cache_dir):
                filepath = os.path.join(self.cache_dir, filename)
                if os.path.isfile(filepath):
                    file_count += 1
                    total_size += os.path.getsize(filepath)
            
            return (file_count, total_size)
            
        except Exception as e:
            debug_print(f"❌ Error getting cache size: {e}")
            return (0, 0)
    
    def cleanup_old_cache(self, max_age_days: int = 7):
        """
        Remove cached thumbnails older than max_age_days
        
        Args:
            max_age_days: Maximum age in days
        """
        try:
            if not os.path.exists(self.cache_dir):
                return
            
            cutoff_time = datetime.now() - timedelta(days=max_age_days)
            removed_count = 0
            
            for filename in os.listdir(self.cache_dir):
                filepath = os.path.join(self.cache_dir, filename)
                
                if not os.path.isfile(filepath):
                    continue
                
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                if mtime < cutoff_time:
                    os.remove(filepath)
                    removed_count += 1
            
            if removed_count > 0:
                debug_print(f"🗑️ Cleaned up {removed_count} old cache files")
            
        except Exception as e:
            debug_print(f"❌ Error cleaning cache: {e}")


class ThumbnailCache:
    """
    LRU cache for thumbnails
    
    Two-level cache:
    1. Memory (fast, limited size)
    2. Disk (persistent, larger)
    """
    
    def __init__(self, cache_dir=None, max_memory_mb=50, max_disk_mb=500):
        """
        Initialize cache
        
        Args:
            cache_dir: Cache directory
            max_memory_mb: Max memory cache size in MB
            max_disk_mb: Max disk cache size in MB
        """
        self.generator = ThumbnailGenerator(cache_dir)
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.max_disk_bytes = max_disk_mb * 1024 * 1024
        
        debug_print(f"💾 ThumbnailCache initialized")
        debug_print(f"   Memory limit: {max_memory_mb} MB")
        debug_print(f"   Disk limit: {max_disk_mb} MB")
    
    def get(self, asset_path: str, asset_format: str = None) -> QtGui.QPixmap:
        """Get thumbnail (uses generator with caching)"""
        return self.generator.get_thumbnail(asset_path, asset_format)
    
    def clear(self):
        """Clear all caches"""
        self.generator.clear_cache()
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        file_count, disk_size = self.generator.get_cache_size()
        memory_count = len(self.generator.memory_cache)
        
        return {
            'memory_items': memory_count,
            'disk_items': file_count,
            'disk_size_bytes': disk_size,
            'disk_size_mb': round(disk_size / (1024 * 1024), 2),
            'cache_dir': self.generator.cache_dir
        }
    
    def cleanup(self, max_age_days: int = 7):
        """Cleanup old cache files"""
        self.generator.cleanup_old_cache(max_age_days)


# Background thumbnail generation (Phase 3 - Advanced)
class ThumbnailWorker(QtCore.QThread):
    """
    Background worker for thumbnail generation
    
    Phase 3: Generate thumbnails in background without blocking UI
    """
    
    # Signals
    thumbnail_ready = QtCore.Signal(str, QtGui.QPixmap)  # (asset_path, pixmap)
    progress = QtCore.Signal(int, int)  # (current, total)
    finished = QtCore.Signal()
    
    def __init__(self, asset_paths, generator):
        """
        Initialize worker
        
        Args:
            asset_paths: List of asset paths to generate thumbnails for
            generator: ThumbnailGenerator instance
        """
        super().__init__()
        self.asset_paths = asset_paths
        self.generator = generator
        self.is_cancelled = False
    
    def run(self):
        """Run thumbnail generation in background"""
        try:
            total = len(self.asset_paths)
            
            for i, asset_path in enumerate(self.asset_paths):
                if self.is_cancelled:
                    debug_print("⏹️ Thumbnail generation cancelled")
                    break
                
                # Get format
                asset_format = os.path.splitext(asset_path)[1].lstrip('.').lower()
                
                # Generate thumbnail
                pixmap = self.generator.get_thumbnail(asset_path, asset_format)
                
                # Emit signals
                self.thumbnail_ready.emit(asset_path, pixmap)
                self.progress.emit(i + 1, total)
                
                debug_print(f"🖼️ Generated {i+1}/{total}: {os.path.basename(asset_path)}")
            
            self.finished.emit()
            debug_print(f"✅ Thumbnail generation complete")
            
        except Exception as e:
            debug_print(f"❌ Worker error: {e}")
            self.finished.emit()
    
    def cancel(self):
        """Cancel thumbnail generation"""
        self.is_cancelled = True


# Convenience functions

def get_thumbnail(asset_path: str, size: int = 256) -> QtGui.QPixmap:
    """
    Get thumbnail for asset (convenience function)
    
    Args:
        asset_path: Path to asset file
        size: Thumbnail size
        
    Returns:
        QPixmap with thumbnail
    """
    generator = ThumbnailGenerator(size=size)
    asset_format = os.path.splitext(asset_path)[1].lstrip('.').lower()
    return generator.get_thumbnail(asset_path, asset_format)

def clear_thumbnail_cache():
    """Clear all cached thumbnails"""
    generator = ThumbnailGenerator()
    generator.clear_cache()

def get_cache_stats() -> dict:
    """Get cache statistics"""
    cache = ThumbnailCache()
    return cache.get_stats()
