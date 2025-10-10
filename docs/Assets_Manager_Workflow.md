# Assets Manager - Workflow & Integration Patterns

**Quick Reference for Development**  
**Version**: 1.0.0  
**Date**: 2025-01-10

---

## 🎯 Core Concepts

### Three-Tool Ecosystem

```
┌─────────────────────────────────────────────────────────────┐
│                    MonoStudio Toolkit                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
│  │ File Manager │   │   Assets     │   │  Material    │    │
│  │              │   │   Manager    │   │  Loader      │    │
│  ├──────────────┤   ├──────────────┤   ├──────────────┤    │
│  │ Working      │   │ Published    │   │ Texture to   │    │
│  │ Scene Files  │   │ Assets       │   │ Materials    │    │
│  │ (.hip)       │   │ (USD/FBX)    │   │ (Redshift/   │    │
│  │              │   │              │   │  Karma)      │    │
│  │ • Quick      │   │ • Browse     │   │              │    │
│  │   switching  │   │ • Preview    │   │ • Auto-      │    │
│  │ • Version    │   │ • Import     │   │   detect     │    │
│  │   management │   │ • Reference  │   │ • UDIM       │    │
│  │ • MiniBar    │   │ • Metadata   │   │   support    │    │
│  └──────────────┘   └──────────────┘   └──────────────┘    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Typical Workflows

### Workflow 1: Character Asset Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│  MODELING                                                     │
└─────────────────────────────────────────────────────────────┘

1. Artist opens File Manager
   └─> Select: _characters / char_hero / 01_modeling
   └─> Open: char_hero_modeling_v004.hip

2. Model character in Houdini
   └─> Iterate, refine geometry
   └─> Save versions (💾 button in MiniBar)

3. Export to _publish/
   └─> Export USD: char_hero_model_v003.usd
   └─> Generate metadata.json:
       {
         "asset_name": "char_hero",
         "version": "v003",
         "department": "modeling",
         "description": "Hero character - final topology",
         "tags": ["character", "hero", "final"],
         "polycount": 45230
       }

┌─────────────────────────────────────────────────────────────┐
│  RIGGING                                                      │
└─────────────────────────────────────────────────────────────┘

4. Rigger opens Assets Manager
   └─> Browse: _characters → char_hero
   └─> Filter: department="modeling", version="v003"
   └─> Preview: See thumbnail, polycount, metadata
   └─> Import: USD Reference (non-destructive)

5. Rigger opens File Manager
   └─> Create new: char_hero_rigging_v001.hip (📄 button)
   └─> Model is already referenced in scene

6. Build rig in Houdini
   └─> Add bones, controls, constraints
   └─> Test deformations

7. Export to _publish/
   └─> Export FBX: char_hero_rig_v002.fbx
   └─> Generate metadata.json:
       {
         "asset_name": "char_hero_rig",
         "version": "v002",
         "department": "rigging",
         "dependencies": ["char_hero_model_v003.usd"],
         "rig_type": "biped",
         "facial_rig": true
       }

┌─────────────────────────────────────────────────────────────┐
│  ANIMATION                                                    │
└─────────────────────────────────────────────────────────────┘

8. Animator opens Assets Manager
   └─> Browse: _characters → char_hero_rig
   └─> Import: char_hero_rig_v002.fbx (USD Reference)

9. Animator opens File Manager
   └─> Create shot: Sh010_animation_v001.hip
   └─> Rig is already in scene

10. Animate character
    └─> Create animation
    └─> Export animation cache if needed
```

---

### Workflow 2: Environment Setup

```
┌─────────────────────────────────────────────────────────────┐
│  LIGHTING ARTIST - ENVIRONMENT SETUP                          │
└─────────────────────────────────────────────────────────────┘

1. Artist opens File Manager
   └─> Select: 02_shots / 03_lighting / Sh020
   └─> Create new: Sh020_lighting_v001.hip

2. Open Assets Manager (⚙️ from MiniBar or Menu)
   └─> Filter: asset_type="_environments"
   └─> Multi-select (Ctrl+Click):
       ✓ env_forest_v002.usd
       ✓ env_rocks_v001.usd
       ✓ env_trees_v003.usd
       ✓ env_grass_v001.abc

3. Batch Import
   └─> Import Mode: USD Reference (all)
   └─> Target: /obj/environment/
   └─> Result: 4 assets referenced in scene
   └─> Scene file size: Small (only references, not full geometry)

4. Add more assets as needed
   └─> Assets Manager: Filter by "props"
   └─> Import: prop_lantern_v001.usd
   └─> Import: prop_bench_v002.usd

5. Layout scene
   └─> Position assets
   └─> Add lights, cameras

6. If asset updates:
   └─> Assets Manager: Select env_forest
   └─> See: New version v003 available
   └─> Update: Click "Update Reference"
   └─> Scene automatically uses new version!

Benefits:
- Fast scene setup (references, not full imports)
- Automatic updates when assets republish
- Small scene files
- Easy to swap asset versions
```

---

### Workflow 3: Texture to Material Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│  SURFACING - TEXTURE TO MATERIAL                              │
└─────────────────────────────────────────────────────────────┘

1. Surfacing artist receives textures
   └─> Textures in: 01_assets/_characters/char_hero/03_surfacing/textures/
       - char_hero_basecolor_1001.png
       - char_hero_basecolor_1002.png
       - char_hero_roughness_1001.png
       - char_hero_normal_1001.png

2. Artist opens Material Loader
   └─> Select texture folder
   └─> Enable UDIM
   └─> Choose renderer: Redshift
   └─> Click "Create Materials"
   └─> Result: Materials auto-created in /mat

3. Apply materials to geometry
   └─> Material already connected to character

4. Export material library
   └─> Export to: _publish/char_hero_materials_v001.usd
   └─> Include metadata.json:
       {
         "asset_name": "char_hero_materials",
         "version": "v001",
         "department": "surfacing",
         "renderer": "redshift",
         "udim": true,
         "texture_count": 12
       }

5. Lighting artist uses Assets Manager
   └─> Browse: _characters → char_hero
   └─> Filter: department="surfacing"
   └─> Import: char_hero_materials_v001.usd (sublayer)
   └─> Materials appear in scene automatically
```

---

## 🔗 Integration Patterns

### Pattern 1: Cross-Tool Navigation

**From File Manager → Assets Manager**
```python
# In File Manager context menu
def open_published_assets():
    """Open Assets Manager for current asset"""
    # Get current context
    asset_name = get_current_asset_name()  # e.g., "char_hero"
    asset_type = get_current_asset_type()  # e.g., "_characters"
    department = get_current_department()  # e.g., "01_modeling"
    
    # Open Assets Manager with filter
    from mono_tools.assets_manager import show_mono_assets_manager
    browser = show_mono_assets_manager()
    browser.set_filter(
        asset_type=asset_type,
        asset_name=asset_name,
        department=department
    )
```

**From Assets Manager → File Manager**
```python
# In Assets Manager context menu
def edit_working_file():
    """Open File Manager to edit working file for selected asset"""
    # Get selected asset
    asset = get_selected_asset()  # e.g., char_hero_model_v003.usd
    
    # Parse asset info
    asset_name = "char_hero"
    asset_type = "_characters"
    department = "01_modeling"
    
    # Open File Manager
    from mono_tools.file_manager import show_mono_file_manager
    manager = show_mono_file_manager()
    manager.navigate_to_asset(asset_name, asset_type, department)
```

---

### Pattern 2: Shared Settings

```python
# Both tools read/write to same QSettings
from mono_tools.qt import QtCore

ORG = "Mono"

# File Manager settings
settings_fm = QtCore.QSettings(ORG, "FileManager")
settings_fm.setValue("project_root", "/path/to/projects")
settings_fm.setValue("current_project", "MyProject")

# Assets Manager reads same settings
settings_am = QtCore.QSettings(ORG, "AssetsManager")
project_root = settings_am.value("project_root", "")  # Read from File Manager
current_project = settings_am.value("current_project", "")

# Or read directly from FileManager settings
settings_fm = QtCore.QSettings(ORG, "FileManager")
project_root = settings_fm.value("project_root", "")
```

**Shared Settings:**
- `project_root`: Root of all projects
- `current_project`: Currently active project
- `recent_projects`: List of recent projects
- `minibar_ui_scale`: UI scale factor (80% - 150%)

**Tool-Specific Settings:**
- File Manager: `minibar_locked`, `minibar_offset_x`, `minibar_offset_y`
- Assets Manager: `thumbnail_size`, `view_mode`, `sort_column`, `filter_presets`

---

### Pattern 3: Context Menu Integration

**File Manager Context Menu:**
```python
# Right-click on file in File Manager
[Context Menu]
├─ Open in Houdini
├─ Save Version
├─ Open File Location
├─ Open Render Folder
├─ ──────────────────────
├─ Browse Published Assets  ← Opens Assets Manager
└─ Import Published Asset   ← Quick import from Assets Manager
```

**Assets Manager Context Menu:**
```python
# Right-click on asset in Assets Manager
[Context Menu]
├─ Import
├─ Reference (USD)
├─ Copy Path
├─ Open Location
├─ ──────────────────────
├─ Edit Working File       ← Opens File Manager
└─ View Metadata
```

**Network Editor Context Menu (in Houdini):**
```python
# Right-click in /obj network
[Context Menu]
├─ Create Geometry
├─ Create Light
├─ ──────────────────────
├─ Import Asset from Manager  ← Quick access to Assets Manager
└─ Reference Asset            ← Quick reference from Assets Manager
```

---

### Pattern 4: MiniBar Integration (Optional)

**Assets Manager MiniBar** (Future feature):
```python
# Lightweight version of Assets Manager (like File Manager MiniBar)
# Shows recently used assets
# Quick import/reference without opening full browser

┌────────────────────────────────────────────┐
│ ⋮⋮ | Recent: char_hero_v003.usd | 📥 ⚡ ⚙️ │
└────────────────────────────────────────────┘

Features:
- Recent assets dropdown
- Quick import button (📥)
- Quick menu (⚡): Import, Reference, Copy Path
- Settings button (⚙️): Open full Assets Manager
```

---

## 📁 Directory Structure & Scanning

### Standard Project Structure

```
D:/Projects/MyProject/
├── 01_assets/
│   ├── _characters/
│   │   ├── char_hero/
│   │   │   ├── 01_modeling/
│   │   │   │   ├── char_hero_modeling_v001.hip    ← File Manager
│   │   │   │   ├── char_hero_modeling_v002.hip
│   │   │   │   ├── Vers/                          ← Old versions
│   │   │   │   └── _publish/                      ← Assets Manager
│   │   │   │       ├── char_hero_v001.usd
│   │   │   │       ├── char_hero_v002.usd
│   │   │   │       ├── char_hero_v003.usd         ← Latest
│   │   │   │       ├── metadata.json
│   │   │   │       └── thumbnails/
│   │   │   │           └── char_hero_v003_thumb.jpg
│   │   │   ├── 02_rigging/
│   │   │   │   ├── char_hero_rigging_v001.hip     ← File Manager
│   │   │   │   └── _publish/                      ← Assets Manager
│   │   │   │       ├── char_hero_rig_v001.fbx
│   │   │   │       ├── char_hero_rig_v002.fbx
│   │   │   │       └── metadata.json
│   │   │   └── 03_surfacing/
│   │   │       ├── char_hero_surfacing_v001.hip   ← File Manager
│   │   │       ├── textures/
│   │   │       │   ├── char_hero_basecolor_1001.png
│   │   │       │   └── char_hero_normal_1001.png
│   │   │       └── _publish/                      ← Assets Manager
│   │   │           ├── char_hero_materials_v001.usd
│   │   │           └── metadata.json
│   │   │
│   │   └── char_villain/
│   │       └── ... (same structure)
│   │
│   ├── _props/
│   │   ├── prop_chair/
│   │   │   └── ... (same structure)
│   │   └── prop_table/
│   │       └── ... (same structure)
│   │
│   └── _environments/
│       ├── env_forest/
│       │   └── ... (same structure)
│       └── env_city/
│           └── ... (same structure)
│
├── 02_shots/
│   ├── 01_layout/
│   │   ├── Sh010_layout_v001.hip              ← File Manager
│   │   └── Sh010_layout_v002.hip
│   ├── 02_animation/
│   │   ├── Sh010_animation_v001.hip           ← File Manager
│   │   └── _publish/                          ← Assets Manager
│   │       ├── Sh010_animation_v001.abc
│   │       └── metadata.json
│   └── 03_lighting/
│       ├── Sh010_lighting_v001.hip            ← File Manager
│       ├── Sh020_lighting_v001.hip
│       └── _publish/                          ← Assets Manager
│           ├── Sh010_lighting_v001.usd
│           └── metadata.json
│
├── render/
│   └── Final/
│       ├── Sh010_lighting_v001/
│       └── Sh020_lighting_v001/
│
└── config/
    ├── file_manager/
    │   └── settings.json
    └── assets_manager/
        ├── asset_cache.db
        ├── thumbnails/
        └── settings.json
```

### Scanning Logic

**File Manager Scan** (Working Files):
```python
# Scan ONLY .hip files (not in _publish/)
scan_patterns = [
    "01_assets/*/asset_name/department/*.hip",  # Assets
    "02_shots/department/*.hip"                  # Shots
]

ignore_folders = [
    "_publish",      # Published assets (Assets Manager)
    "backup",        # Backup folders
    "Vers",          # Old versions
    "old",           # Old work
    ".git",          # Git repo
    "__pycache__",   # Python cache
    "_thumbnail"     # Thumbnail cache
]
```

**Assets Manager Scan** (Published Assets):
```python
# Scan ONLY _publish/ folders
scan_patterns = [
    "01_assets/*/asset_name/department/_publish/*",  # Asset publishes
    "02_shots/department/_publish/*"                  # Shot publishes
]

asset_formats = [
    '.fbx', '.obj',                                   # Geometry
    '.usd', '.usda', '.usdc',                         # USD
    '.abc',                                           # Alembic
    '.bgeo', '.bgeo.sc',                              # Houdini geo
    '.vdb',                                           # VDB volumes
    '.hda',                                           # Digital assets
    '.mtlx',                                          # MaterialX
    # Textures (optional, usually referenced not browsed)
    '.jpg', '.png', '.exr', '.tif'
]

ignore_folders = [
    "backup",
    "old",
    "Vers",
    "__pycache__"
]
```

---

## 🚀 Quick Reference: Common Operations

### File Manager Operations

```python
from mono_tools.file_manager import show_mono_file_manager, show_mono_minibar

# Show MiniBar (auto-started on Houdini launch)
minibar = show_mono_minibar()

# Show Settings Dialog
manager = show_mono_file_manager()

# Programmatic operations
from mono_tools.file_manager.file_manager_helpers import (
    increment_version_and_backup,
    get_current_houdini_file,
    open_in_explorer
)

# Save version with note
success, new_file, msg = increment_version_and_backup(
    current_file=hou.hipFile.name(),
    note="Fixed lighting bug"
)

# Get current file info
current = get_current_houdini_file()
print(f"Current file: {current}")

# Open file location
open_in_explorer(current)
```

### Assets Manager Operations (Future)

```python
from mono_tools.assets_manager import (
    show_mono_assets_manager,
    import_asset,
    reference_asset,
    search_assets
)

# Show Assets Manager
browser = show_mono_assets_manager()

# Import asset
import_asset(
    asset_path="/path/to/char_hero_v003.usd",
    mode="usd_reference",
    target="/obj/char_hero_001"
)

# Reference asset (non-destructive)
reference_asset(
    asset_path="/path/to/env_forest_v002.usd",
    reference_type="usd_reference"
)

# Search assets
results = search_assets(
    project_path="/path/to/project",
    search_text="hero",
    asset_type="_characters",
    file_format="usd",
    department="modeling"
)

for asset in results:
    print(f"Found: {asset['filename']} (v{asset['version']})")
```

### Material Loader Operations

```python
from mono_tools.material_loader import show_material_loader

# Show Material Loader dialog
loader = show_material_loader()

# Programmatic material creation (if backend available)
from Mono_MaterialLoader import create_usd_rs_materials_by_prefix

materials = create_usd_rs_materials_by_prefix(
    texture_dir="/path/to/textures",
    material_library="/mat",
    udim_enabled=True
)
```

---

## 🔄 Data Flow Examples

### Example 1: Simple Asset Import

```
User Action:
    Click "Import" on char_hero_v003.usd in Assets Manager

Data Flow:
    1. Assets Manager → Get asset metadata from database
    2. Assets Manager → Show import options dialog
    3. User selects: USD Reference, target=/obj/char_hero_001
    4. Assets Manager → Call importer.import_usd_asset()
    5. Importer → Create USD reference node in Houdini
    6. Importer → Set file path parameter
    7. Importer → Resolve dependencies (textures, materials)
    8. Houdini → Load geometry
    9. Assets Manager → Update recent assets
    10. Assets Manager → Update database (access time)

Result:
    - Asset appears in Houdini scene at /obj/char_hero_001
    - Asset is referenced (not merged)
    - If source file updates, scene updates automatically
```

### Example 2: Cross-Tool Workflow

```
User Workflow:
    1. Working in File Manager → char_hero_modeling_v005.hip
    2. Right-click file → "Browse Published Assets"
    3. Assets Manager opens, filtered to char_hero / modeling
    4. See all published versions (v001 - v003)
    5. Select v002 → Preview old version
    6. Click "Import" → Load into current scene for comparison
    7. Back to File Manager → Continue working on v005

Data Flow:
    File Manager → Assets Manager:
        - Pass context: asset_name="char_hero", department="modeling"
    
    Assets Manager:
        - Query database: SELECT * WHERE asset_name='char_hero' AND department='modeling'
        - Display results
        - User selects asset
        - Import into Houdini
    
    Back to File Manager:
        - No explicit return needed
        - Both tools independent
        - User continues work
```

---

## 💡 Tips & Best Practices

### For Artists

**File Naming:**
```
✅ Good:
- char_hero_modeling_v003.hip       (working file)
- char_hero_v003.usd                (published asset)
- prop_chair_v001.fbx               (published asset)
- env_forest_v002.abc               (published asset)

❌ Bad:
- hero_final_FINAL_v2_new.hip      (unclear version)
- char.usd                          (no version)
- model_123.fbx                     (no asset name)
```

**Publishing:**
```
Always publish to _publish/ folder:
01_assets/_characters/char_hero/01_modeling/
├── char_hero_modeling_v003.hip    ← Working file (File Manager)
└── _publish/
    ├── char_hero_v003.usd         ← Published (Assets Manager)
    ├── char_hero_v003.fbx         ← Alternative format
    ├── metadata.json              ← Metadata
    └── thumbnails/
        └── char_hero_v003_thumb.jpg
```

**Version Management:**
```
Working files (File Manager):
- Save frequently
- Use "Save Version" (💾 button) for milestones
- Old versions go to Vers/ folder automatically

Published assets (Manual):
- Export to _publish/ when ready
- Increment version number manually
- Add metadata.json for better organization
```

### For TDs

**Database Maintenance:**
```python
# Regular maintenance (weekly/monthly)
from mono_tools.assets_manager import database

# Re-scan project (detect new assets)
database.scan_project(force=True)

# Clean up orphaned thumbnails
database.cleanup_thumbnails()

# Optimize database
database.vacuum()

# Backup database
database.backup(backup_path="backups/asset_cache_2025_01_10.db")
```

**Custom Workflows:**
```python
# Custom import function
def smart_import_character(char_name):
    """Import character with all dependencies"""
    from mono_tools.assets_manager import search_assets, import_asset
    
    # Find latest model
    model = search_assets(
        asset_name=char_name,
        department="modeling",
        sort_by="version",
        limit=1
    )[0]
    
    # Find latest rig
    rig = search_assets(
        asset_name=f"{char_name}_rig",
        department="rigging",
        sort_by="version",
        limit=1
    )[0]
    
    # Import both
    import_asset(model['filepath'], mode="usd_reference")
    import_asset(rig['filepath'], mode="usd_reference")
    
    print(f"Imported {char_name}: model v{model['version']}, rig v{rig['version']}")

# Usage
smart_import_character("char_hero")
```

---

## 📊 Performance Tips

### Optimize Asset Scanning

```python
# Parallel scanning (faster for large projects)
from multiprocessing import Pool

def scan_folder(folder_path):
    """Scan single folder"""
    return collect_files(folder_path)

# Scan multiple folders in parallel
folders = ["01_assets/_characters", "01_assets/_props", "01_assets/_environments"]
with Pool(processes=4) as pool:
    results = pool.map(scan_folder, folders)
```

### Optimize Thumbnail Loading

```python
# Lazy loading strategy
class ThumbnailGrid(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.visible_items = []
        self.all_items = []
    
    def update_visible_items(self):
        """Only load thumbnails for visible items"""
        viewport_rect = self.viewport().rect()
        
        for item in self.all_items:
            if item.geometry().intersects(viewport_rect):
                if item not in self.visible_items:
                    # Item became visible, load thumbnail
                    self.load_thumbnail(item)
                    self.visible_items.append(item)
            else:
                if item in self.visible_items:
                    # Item no longer visible, unload thumbnail
                    self.unload_thumbnail(item)
                    self.visible_items.remove(item)
```

### Cache Strategy

```python
# Two-level cache: Memory + Disk
class ThumbnailCache:
    def __init__(self, max_memory_items=100):
        self.memory_cache = {}  # LRU cache (fast)
        self.disk_cache_path = "config/assets_manager/thumbnails/"
        self.max_memory_items = max_memory_items
    
    def get_thumbnail(self, asset_path, size=256):
        """Get thumbnail from cache or generate"""
        # Check memory cache first
        cache_key = f"{asset_path}_{size}"
        if cache_key in self.memory_cache:
            return self.memory_cache[cache_key]
        
        # Check disk cache
        disk_path = self.get_disk_cache_path(asset_path, size)
        if os.path.exists(disk_path):
            thumbnail = QtGui.QPixmap(disk_path)
            self.memory_cache[cache_key] = thumbnail
            return thumbnail
        
        # Generate new thumbnail
        thumbnail = self.generate_thumbnail(asset_path, size)
        
        # Save to both caches
        thumbnail.save(disk_path)
        self.memory_cache[cache_key] = thumbnail
        
        # Cleanup memory cache if too large
        if len(self.memory_cache) > self.max_memory_items:
            # Remove oldest items (LRU)
            oldest_key = next(iter(self.memory_cache))
            del self.memory_cache[oldest_key]
        
        return thumbnail
```

---

**Last Updated**: 2025-01-10  
**Version**: 1.0.0  
**Status**: 📋 Ready for Implementation


