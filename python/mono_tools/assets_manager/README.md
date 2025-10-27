# Assets Manager

**Published Asset Browser for Houdini**

Browse, preview, and import published assets (USD, FBX, ABC, etc.) from `_publish/` directories in your Houdini pipeline.

## Status

**Phase 1: Core Foundation** ✅ Complete
- ✅ Database (SQLite)
- ✅ Scanner (scan _publish/ folders)
- ✅ Metadata parser (JSON)
- ✅ All tests passing (5/5)

**Phase 2: Basic UI** ✅ Complete
- ✅ Main dialog (1024x768)
- ✅ Asset browser (list view)
- ✅ Preview panel
- ✅ Search & filters
- ✅ All tests passing (4/4)

**Future Phases:**
- Phase 3: Thumbnails (🔜 Next)
- Phase 4: Import/Reference
- Phase 5: Advanced Features
- Phase 6: Integration & Polish

**Overall Progress: 33.3% (2/6 phases complete)**

## Installation

Assets Manager is part of MonoStudio v2.2.0+. No separate installation needed.

## Usage

### Phase 2: Show UI (Houdini or Standalone)

```python
# In Houdini Python console
from mono_tools.assets_manager import show_mono_assets_manager
show_mono_assets_manager()

# Or standalone (if PySide6 installed)
python -c "from mono_tools.assets_manager import show_mono_assets_manager; show_mono_assets_manager()"
```

### Phase 1 Usage (Command Line / Python Console)

### 1. Database Operations

```python
from mono_tools.assets_manager import AssetDatabase

# Create database
db = AssetDatabase()

# Add an asset
asset_data = {
    'filepath': '/path/to/asset.usd',
    'filename': 'char_hero_v003.usd',
    'asset_name': 'char_hero',
    'asset_type': '_characters',
    'department': '01_modeling',
    'file_format': 'usd',
    'file_size': 1024000,
    'version': 'v003'
}
asset_id = db.add_asset(asset_data)

# Search assets
results = db.search_assets(
    search_text='hero',
    asset_type='_characters',
    file_format='usd'
)

# Get statistics
stats = db.get_stats()
print(f"Total assets: {stats['total_assets']}")
```

### 2. Scanner Operations

```python
from mono_tools.assets_manager import AssetScanner

# Scan project
scanner = AssetScanner('/path/to/project')
assets = scanner.scan_project()

print(f"Found {len(assets)} assets")

# Get scan statistics
stats = scanner.get_stats()
print(f"Scan time: {stats['scan_time']:.2f}s")
print(f"By format: {stats['by_format']}")

# Filter results
usd_assets = scanner.filter_by_format('usd')
character_assets = scanner.filter_by_type('_characters')
```

### 3. Metadata Operations

```python
from mono_tools.assets_manager import MetadataManager

# Read metadata
manager = MetadataManager()
metadata = manager.read_metadata('/path/to/asset.usd')

# Create metadata template
template = manager.create_metadata_template('/path/to/asset.usd')

# Write metadata
manager.write_metadata_json('/path/to/metadata.json', template)

# Validate metadata
is_valid, errors = manager.validate_metadata(metadata)
if not is_valid:
    print(f"Metadata errors: {errors}")
```

### 4. Complete Workflow

```python
from mono_tools.assets_manager import AssetScanner, AssetDatabase, MetadataManager

# 1. Scan project
scanner = AssetScanner('/path/to/project')
assets = scanner.scan_project()

# 2. Open database
db = AssetDatabase()

# 3. Add assets to database
metadata_mgr = MetadataManager()
for asset in assets:
    # Try to load metadata
    metadata = metadata_mgr.read_metadata(asset['filepath'])
    asset['metadata'] = metadata
    
    # Add to database
    db.add_asset(asset)

# 4. Search
results = db.search_assets(search_text='hero')
for result in results:
    print(f"{result['filename']} - {result['version']}")

# 5. Get stats
stats = db.get_stats()
print(f"Total assets: {stats['total_assets']}")
print(f"Database size: {stats['db_size_mb']} MB")
```

## Supported File Formats

### Geometry
- `.fbx` - FBX
- `.obj` - Wavefront OBJ
- `.abc` - Alembic
- `.usd`, `.usda`, `.usdc` - USD
- `.bgeo`, `.bgeo.sc` - Houdini Geometry

### Textures
- `.jpg`, `.jpeg`, `.png`, `.tga` - Common formats
- `.exr`, `.tif`, `.tiff` - High dynamic range
- `.hdr`, `.hdri` - HDRI

### Cache
- `.vdb` - OpenVDB volumes
- `.pc2` - Point cache

### Materials
- `.mtlx` - MaterialX
- `.hda` - Houdini Digital Asset

## Directory Structure

Assets Manager scans the following structure:

```
project/
├── 01_assets/
│   ├── _characters/
│   │   ├── char_hero/
│   │   │   ├── 01_modeling/
│   │   │   │   └── _publish/        ← Scans here
│   │   │   │       ├── char_hero_v003.usd
│   │   │   │       ├── char_hero_v003.fbx
│   │   │   │       └── metadata.json
│   │   │   └── 02_rigging/
│   │   │       └── _publish/        ← Scans here
│   │   └── char_villain/
│   ├── _props/
│   │   └── prop_chair/
│   │       └── 01_modeling/
│   │           └── _publish/        ← Scans here
│   └── _environments/
└── 02_shots/
    ├── 01_layout/
    │   └── _publish/                ← Scans here
    └── 03_lighting/
        └── _publish/                ← Scans here
```

## Metadata Format

Standard `metadata.json` format:

```json
{
    "asset_name": "char_hero",
    "filename": "char_hero_v003.usd",
    "version": "v003",
    "created_date": "2025-01-09T10:30:00",
    "modified_date": "2025-01-09T15:45:00",
    "created_by": "artist_name",
    "description": "Main hero character - final model",
    "tags": ["character", "hero", "final"],
    "dependencies": [
        "textures/char_hero_basecolor.png"
    ],
    "thumbnail": "char_hero_v003_thumb.jpg",
    "polycount": 45230,
    "bounds": [1.2, 2.0, 0.8],
    "custom": {
        "rig_type": "biped",
        "facial_rig": true
    }
}
```

## Database Location

Default database location:
```
config/assets_manager/asset_cache.db
```

To use a custom location:
```python
db = AssetDatabase('/path/to/custom.db')
```

## Performance

Phase 1 performance (tested with sample projects):

| Operation | < 100 assets | < 1000 assets | Notes |
|-----------|--------------|---------------|-------|
| Initial scan | < 2s | < 15s | Without metadata |
| With metadata | < 5s | < 30s | Reading JSON files |
| Database search | < 50ms | < 100ms | With indexes |
| Add asset | < 10ms | < 10ms | Single insert |

## Debugging

Enable debug output:
```bash
# Windows PowerShell
$env:MONO_DEBUG = "1"

# Linux/Mac
export MONO_DEBUG=1
```

Then run scanner/database operations to see detailed logs.

## API Reference

### AssetDatabase

```python
# Initialize
db = AssetDatabase(db_path=None)

# Operations
asset_id = db.add_asset(asset_data: Dict) -> int
asset = db.get_asset(asset_id: int) -> Optional[Dict]
asset = db.get_asset_by_path(filepath: str) -> Optional[Dict]
results = db.search_assets(search_text=None, asset_type=None, ...) -> List[Dict]

# Utilities
types = db.get_all_asset_types() -> List[str]
formats = db.get_all_file_formats() -> List[str]
stats = db.get_stats() -> Dict
db.vacuum()  # Optimize database
db.clear_all()  # Clear all data (caution!)
```

### AssetScanner

```python
# Initialize
scanner = AssetScanner(project_path: str)

# Scan
assets = scanner.scan_project(incremental=False) -> List[Dict]

# Filter
filtered = scanner.filter_by_type(asset_type: str) -> List[Dict]
filtered = scanner.filter_by_format(file_format: str) -> List[Dict]
filtered = scanner.filter_by_name(search_text: str) -> List[Dict]

# Statistics
stats = scanner.get_stats() -> Dict
```

### MetadataManager

```python
# Initialize
manager = MetadataManager()

# Read/Write
metadata = manager.read_metadata(asset_path: str) -> Dict
success = manager.write_metadata_json(json_path: str, metadata: Dict) -> bool

# Generate
template = manager.create_metadata_template(asset_path: str) -> Dict
default = manager.generate_default_metadata(asset_path: str) -> Dict

# Validate
is_valid, errors = manager.validate_metadata(metadata: Dict) -> Tuple[bool, list]
```

## Troubleshooting

### "Database locked" error
- Close other connections to database
- Check if another process is using the database
- Use `with` statement for auto-cleanup:
  ```python
  with AssetDatabase() as db:
      db.add_asset(...)
  ```

### Scan takes too long
- Use incremental scan (future Phase 2)
- Filter by specific asset types
- Exclude unnecessary folders

### Metadata not found
- Check if `metadata.json` exists in `_publish/` folder
- Use `create_metadata_template()` to generate template
- Metadata is optional - default metadata will be generated

## Future Features

**Phase 2-6 (Coming Soon):**
- UI browser with grid/list view
- Thumbnail generation and caching
- Import/Reference into Houdini
- Advanced filtering and search
- Menu and shelf integration
- Cross-tool integration with File Manager

See [Assets_Manager_Plan.md](../../../docs/Assets_Manager_Plan.md) for complete roadmap.

## Related Tools

- **File Manager**: Working scene files (.hip)
- **Material Loader**: Texture to material creation
- **Texture Search**: Path management

See [MonoStudio_Ecosystem.md](../../../docs/MonoStudio_Ecosystem.md) for complete toolkit overview.

---

**Version**: 1.0.0 (Phase 1)  
**Last Updated**: 2025-01-10  
**Status**: Core Foundation Complete





