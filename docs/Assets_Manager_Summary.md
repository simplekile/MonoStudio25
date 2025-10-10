# Assets Manager - Quick Summary

**One-page overview for quick reference**  
**Version**: 1.0.0 | **Status**: 📋 Planning Phase  

---

## 🎯 What is Assets Manager?

Specialized tool for **browsing, previewing, and importing published assets** (USD, FBX, ABC, textures) from `_publish/` directories in your Houdini pipeline.

**Complement to File Manager**: File Manager handles working `.hip` files, Assets Manager handles published assets.

---

## 🏗️ Core Architecture

```
assets_manager/
├── assets_manager.py              # Main dialog
├── assets_manager_browser.py      # Grid/List view
├── assets_manager_scanner.py      # Scan _publish/ folders
├── assets_manager_importer.py     # Import/Reference into Houdini
├── assets_manager_thumbnails.py   # Thumbnail generation
├── assets_manager_database.py     # SQLite cache
└── assets_manager_metadata.py     # Metadata parsing
```

**Database**: SQLite for asset metadata & search  
**Cache**: Thumbnails in `config/assets_manager/thumbnails/`  
**Formats**: USD, FBX, ABC, OBJ, BGEO, VDB, textures

---

## 🎨 UI Layout

```
┌─────────────────────────────────────────────┐
│ 🔍 Search | Type▾ | Format▾ | Date▾        │
├──────────────────────┬──────────────────────┤
│  GRID/LIST VIEW      │  PREVIEW PANEL       │
│  [Thumbnails]        │  [Large Thumbnail]   │
│  [Asset Names]       │  Metadata            │
│                      │  [Import][Reference] │
└──────────────────────┴──────────────────────┘
```

---

## 🔧 Key Features

| Feature | Description |
|---------|-------------|
| **Browser** | Grid view (thumbnails) + List view (table) |
| **Preview** | Large thumbnail + full metadata |
| **Import** | USD merge, USD reference, FBX import |
| **Reference** | Non-destructive USD/ABC reference |
| **Search** | Fuzzy text search + filters (type, format, date) |
| **Thumbnails** | Auto-generated (background) + cached |
| **Metadata** | Read from JSON or USD, display in panel |
| **Batch Ops** | Multi-select, batch import, batch actions |

---

## 🔄 Integration with File Manager

### Shared
- Project settings (root, current project)
- QSettings (Mono organization)

### Cross-Links
- File Manager → Assets Manager: "Browse Published Assets"
- Assets Manager → File Manager: "Edit Working File"

### Workflow
```
1. Work in File Manager (.hip files)
2. Export to _publish/ folder
3. Browse in Assets Manager
4. Import into new scene
5. Back to File Manager (iterate)
```

---

## 🚀 Quick Start (Planned)

```python
# Show Assets Manager
from mono_tools.assets_manager import show_mono_assets_manager
show_mono_assets_manager()

# Import asset
from mono_tools.assets_manager import import_asset
import_asset("/path/to/asset.usd", mode="usd_reference")

# Search assets
from mono_tools.assets_manager import search_assets
results = search_assets(
    project_path="/path/to/project",
    search_text="hero",
    asset_type="_characters"
)
```

---

## 📁 Directory Structure

```
01_assets/_characters/char_hero/01_modeling/
├── char_hero_modeling_v003.hip     ← File Manager
└── _publish/                       ← Assets Manager
    ├── char_hero_v003.usd          ✅ Browse this
    ├── char_hero_v003.fbx
    ├── metadata.json
    └── thumbnails/
        └── char_hero_v003_thumb.jpg
```

---

## 🎯 Import Modes

| Mode | Use Case | File Types |
|------|----------|------------|
| **USD Reference** | Non-destructive, auto-updates | USD |
| **USD Sublayer** | Layered composition | USD |
| **USD Merge** | Direct import | USD |
| **FBX Import** | Geometry import | FBX |
| **Alembic Cache** | Animation cache | ABC |
| **File SOP** | Procedural reference | All |

---

## 📊 Performance Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| Scan 1000 assets | < 30s | First time, no cache |
| Re-scan | < 2s | Incremental |
| Search/Filter | < 100ms | Database indexed |
| Thumbnail load | < 100ms | From cache |
| Import asset | < 5s | Depends on size |

---

## 🗂️ Metadata Format

```json
{
    "asset_name": "char_hero",
    "version": "v003",
    "asset_type": "_characters",
    "department": "01_modeling",
    "created_date": "2025-01-09T10:30:00",
    "description": "Main hero character",
    "tags": ["character", "hero", "final"],
    "polycount": 45230,
    "dependencies": ["textures/char_hero_basecolor.png"]
}
```

---

## 🚧 Implementation Phases

| Phase | Timeline | Deliverable |
|-------|----------|-------------|
| **Phase 1** | Week 1-2 | Scanner + Database |
| **Phase 2** | Week 3-4 | Basic UI + Browser |
| **Phase 3** | Week 5-6 | Thumbnails + Cache |
| **Phase 4** | Week 7-8 | Import/Reference |
| **Phase 5** | Week 9-10 | Advanced Filters |
| **Phase 6** | Week 11-12 | Polish + Integration |

**Target Launch**: 12 weeks (3 months)

---

## 💡 Key Differences: File Manager vs Assets Manager

| Feature | File Manager | Assets Manager |
|---------|--------------|----------------|
| **Files** | `.hip`, `.hiplc`, `.hipnc` | USD, FBX, ABC, textures |
| **Location** | Working dirs | `_publish/` only |
| **UI** | MiniBar (lightweight) | Browser (rich) |
| **Actions** | Open, Save version | Import, Reference |
| **Performance** | Fast (few files) | Slower (many assets, thumbnails) |
| **Cache** | None (settings only) | SQLite + thumbnails |
| **Startup** | Auto-load MiniBar | Manual open |

---

## 📚 Related Documents

- **Full Plan**: [`Assets_Manager_Plan.md`](./Assets_Manager_Plan.md) - Complete technical design (50+ pages)
- **Workflow Guide**: [`Assets_Manager_Workflow.md`](./Assets_Manager_Workflow.md) - Integration patterns & workflows
- **File Manager README**: [`python/mono_tools/file_manager/README.md`](../python/mono_tools/file_manager/README.md) - Current tool reference

---

## ✅ Next Steps

1. **Review** this summary with team
2. **Confirm** priorities and timeline
3. **Start** Phase 1 implementation (Scanner + Database)
4. **Iterate** based on feedback

---

**Questions?** See full plan document or discuss with team.

**Last Updated**: 2025-01-10  
**Status**: 📋 Awaiting Review


