# Assets Manager - Kế Hoạch Phát Triển

**Version**: 1.0.0 (Planning Phase)  
**Date**: 2025-01-10  
**Status**: 📋 Planning  
**Project**: MonoStudio v2.2.0+

---

## 🎯 Tổng Quan

### Mục Đích
Assets Manager là tool chuyên biệt để **browse, preview và import/reference published assets** trong pipeline Houdini, bổ sung cho File Manager (quản lý working files).

### Separation of Concerns

| Feature | File Manager ✅ | Assets Manager 🔜 |
|---------|----------------|-------------------|
| **Focus** | Daily scene file management | Published asset browsing |
| **Files** | `.hip`, `.hiplc`, `.hipnc` | All formats (FBX, USD, ABC, textures, etc.) |
| **Location** | Working directories | `_publish/` directories |
| **UI** | MiniBar + Settings (lightweight) | Browser + Preview (rich UI) |
| **Performance** | Fast scanning (working files only) | Thumbnails, metadata, filtering |
| **Actions** | Open scene, save version | Import, reference, copy path |

---

## 🏗️ Architecture

### 1. Core Components

```
python/mono_tools/assets_manager/
├── __init__.py                      # Package exports
├── assets_manager.py                # Main browser dialog
├── assets_manager_browser.py        # Grid/List view browser
├── assets_manager_preview.py        # Preview panel (thumbnails, metadata)
├── assets_manager_scanner.py        # Asset scanning & indexing
├── assets_manager_importer.py       # Import/Reference operations
├── assets_manager_metadata.py       # Metadata parsing & caching
├── assets_manager_thumbnails.py     # Thumbnail generation & cache
├── assets_manager_filters.py        # Advanced filtering (type, date, tags)
├── assets_manager_menu_integration.py  # Menu integration
└── README.md                        # Documentation
```

### 2. Database / Cache System

Assets Manager cần cache để performance tốt:

```
config/assets_manager/
├── asset_cache.db                   # SQLite database cho metadata
├── thumbnails/                      # Thumbnail cache
│   ├── char_hero_abc_thumb.jpg
│   ├── prop_chair_fbx_thumb.jpg
│   └── ...
└── recent_assets.json               # Recently accessed assets
```

**Database Schema (SQLite)**:
```sql
CREATE TABLE assets (
    id INTEGER PRIMARY KEY,
    filepath TEXT UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    asset_name TEXT NOT NULL,
    asset_type TEXT,           -- _characters, _props, etc.
    department TEXT,           -- modeling, rigging, etc.
    file_format TEXT,          -- fbx, usd, abc, etc.
    file_size INTEGER,
    created_date TEXT,
    modified_date TEXT,
    version TEXT,
    thumbnail_path TEXT,
    metadata_json TEXT,        -- Additional metadata as JSON
    tags TEXT,                 -- Comma-separated tags
    description TEXT
);

CREATE TABLE recent_assets (
    id INTEGER PRIMARY KEY,
    asset_id INTEGER,
    access_time TEXT,
    FOREIGN KEY(asset_id) REFERENCES assets(id)
);
```

---

## 🎨 UI Design

### Main Dialog Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Assets Manager                                    [_] [□] [X]  │
├─────────────────────────────────────────────────────────────────┤
│ 🔍 Search: [________________]  Type: [All ▾]  Format: [All ▾]  │
│ 📁 Path: D:/Projects/MyProject/01_assets/_characters/          │
├──────────────────────────────┬──────────────────────────────────┤
│                              │                                  │
│   ASSET GRID / LIST VIEW     │    PREVIEW PANEL                 │
│                              │                                  │
│  ┌────┐ ┌────┐ ┌────┐        │    ┌──────────────────┐          │
│  │img │ │img │ │img │        │    │                  │          │
│  └────┘ └────┘ └────┘        │    │   Thumbnail      │          │
│  Hero    Chair   Tree         │    │                  │          │
│                              │    └──────────────────┘          │
│  ┌────┐ ┌────┐ ┌────┐        │                                  │
│  │img │ │img │ │img │        │    Name: char_hero               │
│  └────┘ └────┘ └────┘        │    Type: _characters             │
│  Rock    Lamp   Sword         │    Format: USD                   │
│                              │    Size: 45.2 MB                 │
│  [Grid View] [List View]     │    Modified: 2025-01-09          │
│                              │    Version: v003                 │
│                              │                                  │
│                              │    Tags: [character][hero][final]│
│                              │                                  │
│                              │    Description:                  │
│                              │    Main hero character...        │
│                              │                                  │
│                              │    [Import] [Reference] [Copy]   │
│                              │                                  │
├──────────────────────────────┴──────────────────────────────────┤
│ 📊 234 assets found | 12 filtered | Selected: char_hero.usd     │
└─────────────────────────────────────────────────────────────────┘
```

### Grid View
- Thumbnail grid (configurable size: 128x128, 256x256, 512x512)
- Asset name below thumbnail
- Version badge overlay
- Format icon overlay
- Hover tooltip with quick info

### List View
- Table columns: Icon | Name | Type | Department | Format | Size | Modified | Version
- Sortable by any column
- Quick filtering per column
- Multiselect support

### Preview Panel
- Large thumbnail (512x512 or adaptive)
- Full metadata display
- Recent access history
- Related assets (same type/department)
- Action buttons (Import, Reference, Copy Path, Open Location)

---

## 🔧 Core Features

### 1. Asset Scanning & Indexing

**Scan Strategy:**
```python
# Incremental scanning approach
def scan_assets(project_path, force_rescan=False):
    """
    Scan _publish/ folders for published assets
    
    Structure:
    01_assets/
    ├── _characters/
    │   ├── char_hero/
    │   │   ├── 01_modeling/
    │   │   │   └── _publish/
    │   │   │       ├── char_hero_v003.fbx  ✅ Scan này
    │   │   │       ├── char_hero_v003.usd  ✅ Scan này
    │   │   │       └── metadata.json       ✅ Read metadata
    │   │   └── 02_rigging/
    │   │       └── _publish/
    │   │           └── char_hero_rig_v002.fbx
    
    Performance:
    - Only scan _publish/ folders (skip working files)
    - Use modification time to detect changes
    - Parallel scanning with multiprocessing
    - Progress bar for long scans
    """
    pass

# Supported formats
ASSET_FORMATS = {
    'geometry': ['.fbx', '.obj', '.abc', '.usd', '.usda', '.usdc', '.bgeo', '.bgeo.sc'],
    'texture': ['.jpg', '.jpeg', '.png', '.tga', '.exr', '.tif', '.tiff', '.hdr'],
    'cache': ['.bgeo', '.bgeo.sc', '.vdb', '.abc', '.pc2'],
    'scene': ['.usd', '.usda', '.usdc'],
    'material': ['.mtlx', '.vop', '.hda'],
}
```

**Incremental Updates:**
- Watch file system for changes (optional)
- Background re-scan on startup (low priority)
- Manual refresh button
- Auto-refresh on folder change

### 2. Thumbnail Generation

**Strategy:**
```python
def generate_thumbnail(asset_path, size=256):
    """
    Generate thumbnail for asset
    
    Methods:
    1. USD/ABC: Use Houdini's image generation
       - Load geometry in background COP network
       - Render with standard camera & lights
       - Cache result
    
    2. FBX/OBJ: Use Houdini's geometry viewer
       - Import to temp geometry node
       - Capture viewport thumbnail
       - Clean up temp nodes
    
    3. Textures: Direct image thumbnail
       - Use PIL/Pillow for image formats
       - Generate preview with aspect ratio
    
    4. Fallback: Use file type icon
       - Generic icons for each format
    
    Cache Strategy:
    - Store in config/assets_manager/thumbnails/
    - Filename: {asset_hash}_{size}.jpg
    - TTL: 7 days (re-generate if asset modified)
    """
    pass
```

**Thumbnail Cache:**
- LRU cache (Least Recently Used)
- Max cache size: 500 MB (configurable)
- Background generation (don't block UI)
- Progress indicator for batch generation

### 3. Metadata System

**Standard Metadata:**
```python
# metadata.json in _publish/ folder
{
    "asset_name": "char_hero",
    "asset_type": "_characters",
    "department": "01_modeling",
    "version": "v003",
    "created_date": "2025-01-09T10:30:00",
    "modified_date": "2025-01-09T15:45:00",
    "created_by": "artist_name",
    "description": "Main hero character - final model",
    "tags": ["character", "hero", "final", "rigged"],
    "dependencies": [
        "textures/char_hero_basecolor.png",
        "textures/char_hero_normal.png"
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

**Metadata Parser:**
- Read from `.json`, `.xml`, or embedded in USD
- Auto-generate basic metadata if not present
- User can edit metadata in UI
- Sync back to file when saved

### 4. Import / Reference System

**Import Strategies:**

```python
def import_asset(asset_path, import_mode='merge'):
    """
    Import asset into current Houdini scene
    
    Modes:
    1. merge: Import geometry directly into /obj
    2. sublayer: Add as USD sublayer (for USD files)
    3. reference: Add as USD reference (LOPs)
    4. file_sop: Create File SOP pointing to asset
    5. copy_local: Copy asset to project and import
    
    Smart Import:
    - Auto-detect file format
    - Suggest best import method
    - Handle dependencies (textures, etc.)
    - Preserve transforms and attributes
    """
    pass

def reference_asset(asset_path, reference_type='usd'):
    """
    Reference asset (non-destructive)
    
    Types:
    1. usd_reference: USD reference (standard)
    2. file_cache: Alembic file cache
    3. file_sop: File SOP with reference
    4. packed_prim: Packed primitive reference
    
    Benefits:
    - Original asset unchanged
    - Updates propagate automatically
    - Lighter scene files
    """
    pass
```

**Import Options Dialog:**
```
┌─────────────────────────────────────┐
│  Import Options: char_hero.usd     │
├─────────────────────────────────────┤
│                                     │
│  Import Mode:                       │
│  ○ Merge (direct import)            │
│  ◉ USD Reference (recommended)      │
│  ○ USD Sublayer                     │
│  ○ File SOP                         │
│                                     │
│  Target Location:                   │
│  /obj/[char_hero_001_____]          │
│                                     │
│  ☑ Import textures                  │
│  ☑ Import materials                 │
│  ☐ Create proxy geometry            │
│                                     │
│  Transform:                         │
│  ☑ Preserve original transform      │
│  ☐ Place at origin                  │
│                                     │
│        [Import]      [Cancel]       │
└─────────────────────────────────────┘
```

### 5. Advanced Filtering

**Filter System:**
- **Text Search**: Fuzzy search on name, description, tags
- **Type Filter**: _characters, _props, _environments, etc.
- **Format Filter**: USD, FBX, ABC, etc.
- **Date Range**: Modified/created date range
- **Size Range**: File size filter
- **Version Filter**: Latest only, specific version, all versions
- **Tags Filter**: Multi-tag selection
- **Department Filter**: modeling, rigging, surfacing, etc.

**Saved Filters:**
- Save common filter combinations
- Quick access dropdown
- Share filters with team (JSON export/import)

### 6. Batch Operations

**Batch Features:**
- Multi-select assets (Ctrl+Click, Shift+Click)
- Batch import (with progress)
- Batch thumbnail generation
- Batch metadata edit
- Batch copy to location
- Export asset list (CSV, JSON)

---

## 🔗 Tương Tác Với Houdini

### 1. Integration Points

**Menu Integration:**
```python
# menus/MonoStudio.menus
{
    "mainMenu": [
        {
            "id": "mono_studio_menu",
            "label": "Mono Studio",
            "submenu": [
                {
                    "id": "mono_file_manager",
                    "label": "File Manager",
                    "action": "show_mono_file_manager"
                },
                {
                    "id": "mono_assets_manager",
                    "label": "Assets Manager",
                    "action": "show_mono_assets_manager"
                },
                {
                    "id": "mono_material_loader",
                    "label": "Material Loader",
                    "action": "show_material_loader"
                }
            ]
        }
    ]
}
```

**Shelf Integration:**
```python
# shelves/MonoStudio.shelf
{
    "tools": [
        {
            "name": "assets_manager",
            "label": "Assets",
            "icon": "$MONO_STUDIO/icons/assets_manager.svg",
            "script": "from mono_tools.assets_manager import show_mono_assets_manager\nshow_mono_assets_manager()"
        }
    ]
}
```

**Python API:**
```python
# Public API
from mono_tools.assets_manager import (
    show_mono_assets_manager,      # Show main dialog
    import_asset,                   # Import asset
    reference_asset,                # Reference asset
    scan_assets,                    # Scan for assets
    get_asset_metadata,             # Get metadata
    search_assets,                  # Search assets
)

# Example usage
from mono_tools import assets_manager

# Show browser
browser = assets_manager.show_mono_assets_manager()

# Import asset programmatically
assets_manager.import_asset(
    "/path/to/asset.usd",
    mode="usd_reference",
    target="/obj/import_char_001"
)

# Search assets
results = assets_manager.search_assets(
    project_path="/path/to/project",
    search_text="hero",
    asset_type="_characters",
    file_format="usd"
)
```

### 2. Houdini Node Integration

**Custom Nodes (Optional - Phase 2):**
```python
# Create HDA: MonoAssetReference.hda
# Digital Asset với built-in asset browser
# - Parameter: Asset Path (với browse button)
# - Browse button opens Assets Manager dialog
# - Select asset → auto-populate path
# - Support multiple formats (USD, FBX, ABC)
```

### 3. Context Menu Integration

**Network Editor Context Menu:**
```python
# Right-click in /obj → "Import Asset from Manager"
# Quick access without opening full browser
```

---

## 🔗 Tương Tác Với File Manager

### Integration Strategy

Assets Manager và File Manager **độc lập nhưng có liên kết**:

```python
# Shared settings (QSettings)
ORG = "Mono"
APP_FILE_MANAGER = "FileManager"
APP_ASSETS_MANAGER = "AssetsManager"

# Shared settings:
# - project_root
# - current_project
# - recent_projects

# Assets Manager reads these from File Manager
settings = QtCore.QSettings(ORG, APP_FILE_MANAGER)
project_root = settings.value("project_root", "")
current_project = settings.value("current_project", "")
```

### Cross-Links

**From File Manager to Assets Manager:**
```python
# In File Manager context menu:
# - "Browse Published Assets" → Open Assets Manager for current asset
# - Pass context: asset_type, asset_name, department

def open_assets_manager_for_current(asset_name):
    """Open Assets Manager filtered to current asset"""
    from mono_tools.assets_manager import show_mono_assets_manager
    
    browser = show_mono_assets_manager()
    browser.set_filter(asset_name=asset_name)
```

**From Assets Manager to File Manager:**
```python
# In Assets Manager:
# - "Open Working File" → Open File Manager, load working file for selected asset
# - Useful for editing asset after viewing published version

def open_working_file_for_asset(asset_name, department):
    """Open File Manager to edit working file"""
    from mono_tools.file_manager import show_mono_file_manager
    
    manager = show_mono_file_manager()
    manager.select_asset(asset_name, department)
```

### Workflow Examples

**Workflow 1: Character Pipeline**
```
1. Artist working in File Manager:
   - Open "char_hero_modeling_v005.hip"
   
2. Artist publishes model:
   - Export to _publish/char_hero_v003.usd
   - Add metadata.json
   - Generate thumbnail
   
3. Rigger uses Assets Manager:
   - Browse _characters → char_hero
   - Preview v003 model
   - Import into new rigging scene
   
4. Rigger works in File Manager:
   - "char_hero_rigging_v001.hip"
   - Reference model from Assets Manager
   
5. Rigger publishes rig:
   - Export to _publish/char_hero_rig_v002.fbx
   
6. Animator uses Assets Manager:
   - Browse _characters → char_hero
   - Import rig v002
```

**Workflow 2: Lighting Scene Setup**
```
1. Lighting artist in File Manager:
   - Open "Sh010_lighting_v001.hip"
   
2. Import multiple assets from Assets Manager:
   - Filter: asset_type="_environments"
   - Batch import: env_forest, env_rocks, env_trees
   - All assets referenced (non-destructive)
   
3. Continue working in File Manager:
   - Scene file is small (only references)
   - Assets update automatically if republished
```

---

## 📊 Performance Considerations

### Optimization Strategies

**1. Lazy Loading:**
- Don't load all thumbnails at once
- Load visible thumbnails first
- Background thread for off-screen thumbnails
- Virtual scrolling for large lists

**2. Database Indexing:**
```sql
-- Create indexes for fast queries
CREATE INDEX idx_asset_name ON assets(asset_name);
CREATE INDEX idx_asset_type ON assets(asset_type);
CREATE INDEX idx_file_format ON assets(file_format);
CREATE INDEX idx_modified_date ON assets(modified_date);
CREATE INDEX idx_tags ON assets(tags);
```

**3. Caching Strategy:**
- In-memory cache for current view (LRU)
- Disk cache for thumbnails (persistent)
- Cache invalidation on file modification
- Background cache warming on startup

**4. Parallel Processing:**
- Multi-threaded thumbnail generation
- Parallel asset scanning (per type/department)
- Async database queries
- Background metadata parsing

### Expected Performance

| Operation | Target | Notes |
|-----------|--------|-------|
| Initial scan (100 assets) | < 5s | With existing cache |
| Initial scan (1000 assets) | < 30s | First time, no cache |
| Re-scan (incremental) | < 2s | Only modified files |
| Thumbnail load (visible) | < 100ms | From cache |
| Thumbnail generate (USD) | 1-3s | Background thread |
| Search/Filter | < 100ms | Database indexed |
| Import asset | 500ms - 5s | Depends on file size |

---

## 🗂️ File Structure

### Complete Module Layout

```
python/mono_tools/assets_manager/
├── __init__.py                          # Package exports
│   - show_mono_assets_manager()
│   - import_asset()
│   - reference_asset()
│   - search_assets()
│
├── assets_manager.py                    # Main dialog
│   - MonoAssetsManager(QDialog)
│   - Coordinates browser, preview, filters
│
├── assets_manager_browser.py            # Grid/List view
│   - AssetBrowserGrid(QWidget)
│   - AssetBrowserList(QTableWidget)
│   - Thumbnail display
│   - Selection handling
│
├── assets_manager_preview.py            # Preview panel
│   - AssetPreviewPanel(QWidget)
│   - Large thumbnail display
│   - Metadata display
│   - Action buttons (Import, Reference, etc.)
│
├── assets_manager_scanner.py            # Asset scanning
│   - AssetScanner
│   - scan_publish_folders()
│   - parse_asset_path()
│   - detect_file_format()
│   - incremental_scan()
│
├── assets_manager_importer.py           # Import/Reference
│   - AssetImporter
│   - import_usd_asset()
│   - import_fbx_asset()
│   - import_abc_asset()
│   - reference_usd_asset()
│   - reference_abc_asset()
│
├── assets_manager_metadata.py           # Metadata handling
│   - MetadataManager
│   - read_metadata_json()
│   - write_metadata_json()
│   - extract_usd_metadata()
│   - generate_default_metadata()
│
├── assets_manager_thumbnails.py         # Thumbnail generation
│   - ThumbnailGenerator
│   - generate_geometry_thumbnail()
│   - generate_texture_thumbnail()
│   - cache_thumbnail()
│   - load_thumbnail_cached()
│
├── assets_manager_database.py           # Database operations
│   - AssetDatabase
│   - create_tables()
│   - add_asset()
│   - update_asset()
│   - search_assets()
│   - get_recent_assets()
│
├── assets_manager_filters.py            # Filtering system
│   - FilterPanel(QWidget)
│   - TextFilter
│   - TypeFilter
│   - FormatFilter
│   - DateRangeFilter
│   - TagFilter
│
├── assets_manager_menu_integration.py   # Menu integration
│   - add_to_menu()
│   - add_to_shelf()
│
└── README.md                            # Documentation

config/assets_manager/
├── asset_cache.db                       # SQLite database
├── thumbnails/                          # Thumbnail cache
│   ├── {hash}_256.jpg
│   └── ...
├── recent_assets.json                   # Recent assets
└── settings.json                        # User preferences

docs/
└── Assets_Manager_Guide.md              # User guide
```

---

## 🚀 Implementation Roadmap

### Phase 1: Core Foundation (Week 1-2)
- [x] Create plan document (this file)
- [ ] Setup folder structure
- [ ] Database schema & SQLite integration
- [ ] Basic asset scanner (scan _publish/ folders)
- [ ] Basic metadata parser (JSON)
- [ ] Simple file format detection

**Deliverable**: Scanner can find and catalog published assets

### Phase 2: Basic UI (Week 3-4)
- [ ] Main dialog layout (QDialog)
- [ ] Asset browser (Grid view only)
- [ ] Preview panel (basic info)
- [ ] Project settings integration (read from File Manager)
- [ ] Basic search/filter (text only)

**Deliverable**: Can browse assets with basic info

### Phase 3: Thumbnails (Week 5-6)
- [ ] Thumbnail generator (geometry)
- [ ] Thumbnail cache system
- [ ] Background thumbnail generation
- [ ] Progress indicator
- [ ] Format-specific icons (fallback)

**Deliverable**: Visual asset browsing with thumbnails

### Phase 4: Import/Reference (Week 7-8)
- [ ] USD import
- [ ] USD reference
- [ ] FBX import
- [ ] Alembic import
- [ ] Import options dialog
- [ ] Error handling

**Deliverable**: Can import assets into Houdini scene

### Phase 5: Advanced Features (Week 9-10)
- [ ] List view (table)
- [ ] Advanced filters (type, format, date, tags)
- [ ] Metadata editing
- [ ] Batch operations
- [ ] Recent assets tracking
- [ ] Copy path / Open location

**Deliverable**: Full-featured asset browser

### Phase 6: Polish & Integration (Week 11-12)
- [ ] Menu integration
- [ ] Shelf integration
- [ ] Cross-link with File Manager
- [ ] Performance optimization
- [ ] User documentation
- [ ] Testing & bug fixes

**Deliverable**: Production-ready tool

### Phase 7: Advanced (Optional - Future)
- [ ] Custom HDA (MonoAssetReference.hda)
- [ ] File system watcher (auto-refresh)
- [ ] Asset version comparison
- [ ] Asset dependencies viewer
- [ ] Team collaboration features (shared tags, ratings)
- [ ] Asset analytics (most used, etc.)

---

## 🧪 Testing Strategy

### Unit Tests
```python
python/mono_tools/test_demo/
├── test_assets_scanner.py              # Scanner tests
├── test_assets_importer.py             # Import tests
├── test_assets_metadata.py             # Metadata tests
├── test_assets_thumbnails.py           # Thumbnail tests
└── test_assets_database.py             # Database tests
```

### Test Cases

**Scanner Tests:**
- Scan empty directory
- Scan with 100 assets
- Scan with nested structure
- Incremental scan (detect changes)
- Ignore non-publish folders

**Importer Tests:**
- Import USD (merge, reference, sublayer)
- Import FBX (with textures)
- Import Alembic (file cache)
- Error handling (missing file)
- Dependency resolution (textures)

**Metadata Tests:**
- Parse valid JSON
- Handle missing metadata
- Generate default metadata
- Write metadata back
- Extract USD metadata

**Thumbnail Tests:**
- Generate geometry thumbnail
- Generate texture thumbnail
- Cache thumbnail (save/load)
- Handle missing thumbnail
- Fallback to format icon

### Integration Tests
- Full workflow: scan → browse → import
- File Manager integration
- Houdini node creation
- Menu/Shelf integration

---

## 📚 User Documentation

### Quick Start Guide

```markdown
# Assets Manager - Quick Start

## What is Assets Manager?

Assets Manager helps you browse, preview, and import **published assets**
(FBX, USD, ABC, textures, etc.) from your project's `_publish/` directories.

## How to Open

1. **Menu**: `Mono Studio → Assets Manager`
2. **Shelf**: Click `Assets` button
3. **Python**: `from mono_tools import assets_manager; assets_manager.show_mono_assets_manager()`

## First Time Setup

1. Open Assets Manager
2. Click "Scan Project" button
3. Wait for initial scan (may take 30s for large projects)
4. Browse assets!

## Browse Assets

- **Grid View**: Visual browsing with thumbnails
- **List View**: Table view with sortable columns
- **Search**: Type to filter by name, tags, description
- **Filters**: Filter by type, format, date, etc.

## Import Asset

1. Select asset from browser
2. Preview metadata in right panel
3. Click "Import" or "Reference" button
4. Choose import options
5. Asset appears in your scene!

## Tips

- Use **Reference** for non-destructive imports (recommended)
- Use **Import** for permanent geometry
- **Ctrl+Click** for multi-select
- **Double-click** to quick import
- Thumbnails generate in background (be patient!)
```

---

## 💡 Best Practices

### For Artists

**Publishing Assets:**
```
1. Finish your asset work
2. Export to _publish/ folder with version:
   - char_hero_v003.usd
   - char_hero_v003.fbx
3. Add metadata.json (optional but recommended)
4. Generate thumbnail (Assets Manager will auto-generate)
5. Test import in new scene
```

**Metadata JSON Example:**
```json
{
    "asset_name": "char_hero",
    "version": "v003",
    "description": "Main hero character - final model",
    "tags": ["character", "hero", "final"],
    "polycount": 45230,
    "created_by": "John Doe"
}
```

### For TDs

**Database Maintenance:**
```python
# Force re-scan (clear cache)
from mono_tools.assets_manager import scanner
scanner.force_rescan(project_path)

# Clear thumbnail cache
import os, shutil
cache_path = "config/assets_manager/thumbnails/"
shutil.rmtree(cache_path)
os.makedirs(cache_path)

# Optimize database
from mono_tools.assets_manager import database
database.vacuum()
```

**Custom Metadata:**
```python
# Add custom fields to metadata
{
    "standard": { ... },
    "custom": {
        "approval_status": "approved",
        "reviewer": "supervisor_name",
        "notes": "Changed arm topology"
    }
}
```

---

## 🔍 Technical Decisions

### Why SQLite?
- **Pros**: 
  - No server required
  - Single file database
  - Fast for < 100K assets
  - Good indexing support
  - Python sqlite3 built-in
- **Cons**:
  - Not ideal for > 100K assets
  - No concurrent write (not an issue for this use case)
- **Alternative**: JSON cache (simpler but slower search)

### Why Not Use USD Metadata Only?
- **Reason**: Not all formats support embedded metadata (FBX, OBJ)
- **Solution**: Separate metadata.json + read from USD when available

### Why Background Thumbnail Generation?
- **Reason**: Geometry loading is slow (1-3s per asset)
- **Solution**: 
  - Load format icons first (instant)
  - Generate thumbnails in background thread
  - Update UI when ready
  - Cache for future use

### Why Separate from File Manager?
- **Reason**: 
  - Different use cases (working files vs published assets)
  - Different performance requirements
  - Different UI patterns (lightweight vs rich)
  - Easier to maintain and test
- **Trade-off**: Slight code duplication (settings, scanning patterns)

---

## 🚧 Known Limitations (v1.0)

### Limitations

1. **No Real-time Updates**: Must manually refresh to see new assets
   - **Workaround**: Click "Refresh" button
   - **Future**: File system watcher (Phase 7)

2. **Thumbnail Generation Slow**: 1-3s per geometry asset
   - **Workaround**: Background generation, be patient
   - **Future**: Pre-generate thumbnails on publish

3. **Large Projects (>1000 assets)**: Initial scan may take 1-2 minutes
   - **Workaround**: Scan runs in background, can browse while scanning
   - **Future**: Incremental scanning, better caching

4. **No Version History View**: Can't compare versions visually
   - **Workaround**: Open multiple versions side-by-side
   - **Future**: Version comparison tool (Phase 7)

5. **No Team Features**: Can't share tags, ratings, comments
   - **Workaround**: Use external tools (Shotgun, Ftrack)
   - **Future**: Cloud sync (Phase 7+)

---

## 📈 Success Metrics

### How to Measure Success

**Performance:**
- Initial scan: < 30s for 1000 assets
- Search/Filter: < 100ms
- Thumbnail load: < 100ms (cached)
- Import asset: < 5s

**Usability:**
- Artist can find asset in < 10 seconds
- Artist can import asset in < 3 clicks
- No crashes or freezes during normal use

**Adoption:**
- 80%+ of team uses Assets Manager regularly
- Positive feedback from artists
- Reduces time spent looking for assets

---

## 🎯 Next Steps

1. **Review this plan** with team/lead
2. **Prioritize features** (what's critical for v1.0?)
3. **Estimate timeline** (realistic deadlines)
4. **Start Phase 1** (core foundation)
5. **Iterate based on feedback**

---

## 📞 Questions & Discussion

### Open Questions

1. **Thumbnail Quality vs Speed**: Higher quality (512x512) or faster generation (128x128)?
   - **Recommendation**: 256x256 default, configurable

2. **Database Location**: Project-specific or global?
   - **Recommendation**: Project-specific (in project root or config/)

3. **Import Target**: Always /obj or let user choose?
   - **Recommendation**: Smart default (/obj/import_ASSETNAME_001) with override option

4. **Metadata Schema**: Fixed or extensible?
   - **Recommendation**: Core fields fixed, custom fields in JSON

5. **Integration with External Tools**: Shotgun, Ftrack, Deadline?
   - **Recommendation**: Phase 7+ (after core features stable)

---

**Version**: 1.0.0 (Planning Phase)  
**Last Updated**: 2025-01-10  
**Status**: 📋 Ready for Review  
**Next**: Team review → Start implementation


