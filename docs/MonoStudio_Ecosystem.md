# MonoStudio Ecosystem Overview

**Complete toolkit for Houdini pipeline management**  
**Version**: 2.2.0  
**Date**: 2025-01-10

---

## 🎯 Vision

MonoStudio provides a **complete, integrated toolkit** for managing assets, files, and materials in a professional Houdini production pipeline.

### Design Philosophy
- **Modular**: Each tool does one thing well
- **Integrated**: Tools work together seamlessly
- **Lightweight**: Fast performance, minimal overhead
- **Professional**: Production-proven workflows

---

## 🏗️ Tool Ecosystem

```
┌──────────────────────────────────────────────────────────────────┐
│                        MonoStudio v2.2.0                          │
│                   Complete Pipeline Toolkit                       │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────┬──────────────────┬─────────┐
│   File Manager   │ Assets Manager   │Material Loader   │ Texture │
│   ✅ Production  │ 📋 Planning      │ ✅ Production    │ Search  │
│                  │                  │                  │ ✅ Prod │
├──────────────────┼──────────────────┼──────────────────┼─────────┤
│                  │                  │                  │         │
│ Working Files    │ Published Assets │ Texture→Material │ Path    │
│ (.hip)           │ (USD/FBX/ABC)    │ (RS/Karma)       │ Replace │
│                  │                  │                  │         │
│ ┌──────────────┐ │ ┌──────────────┐ │ ┌──────────────┐ │ ┌─────┐ │
│ │   MiniBar    │ │ │   Browser    │ │ │Auto-Detect   │ │ │Find │ │
│ │  (Always on) │ │ │  (On-demand) │ │ │   Textures   │ │ │ &   │ │
│ └──────────────┘ │ └──────────────┘ │ └──────────────┘ │ │Repl │ │
│                  │                  │                  │ └─────┘ │
│ • Quick switch   │ • Browse         │ • UDIM support   │ • Regex │
│ • Save version   │ • Preview        │ • Auto-connect   │ • Batch │
│ • Open location  │ • Import         │ • Multiple       │ • Path  │
│ • Restart        │ • Reference      │   renderers      │   mgmt  │
│                  │ • Metadata       │                  │         │
└──────────────────┴──────────────────┴──────────────────┴─────────┘

                          ┌──────────────┐
                          │   Houdini    │
                          │   21.0+      │
                          │   PySide6    │
                          └──────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
              ┌─────▼────┐ ┌────▼─────┐ ┌───▼────┐
              │  Menus   │ │ Shelves  │ │Python  │
              │Integration│ │Integration│ │  API   │
              └──────────┘ └──────────┘ └────────┘
```

---

## 📊 Tool Comparison Matrix

### Feature Comparison

| Feature | File Manager | Assets Manager | Material Loader | Texture Search |
|---------|--------------|----------------|-----------------|----------------|
| **Status** | ✅ Production | 📋 Planning | ✅ Production | ✅ Production |
| **Version** | 2.2.0 | 1.0.0 (plan) | 2.0.0 | 2.0.0 |
| **UI Type** | MiniBar + Dialog | Browser + Preview | Dialog | Dialog |
| **Startup** | Auto (MiniBar) | On-demand | On-demand | On-demand |
| **File Types** | .hip, .hiplc, .hipnc | USD, FBX, ABC, textures | Textures (all formats) | Textures (all) |
| **Location** | Working dirs | _publish/ dirs | Any texture folder | Any node/scene |
| **Database** | None (QSettings) | SQLite | None | None |
| **Cache** | None | Thumbnails + metadata | None | None |
| **Performance** | ⚡ Very fast | 🐢 Medium (thumbnails) | ⚡ Fast | ⚡ Fast |

### Use Case Matrix

| Use Case | Primary Tool | Secondary Tool |
|----------|--------------|----------------|
| Open working file | File Manager | - |
| Save file version | File Manager | - |
| Browse published assets | Assets Manager | - |
| Import asset to scene | Assets Manager | File Manager (context) |
| Create materials from textures | Material Loader | - |
| Fix broken texture paths | Texture Search | - |
| Switch between shots | File Manager (MiniBar) | - |
| Preview asset thumbnail | Assets Manager | - |
| Find asset version | Assets Manager | File Manager |
| Setup lighting scene | Assets Manager (import) | File Manager (open) |

### Integration Matrix

| From Tool | To Tool | Action | How |
|-----------|---------|--------|-----|
| File Manager | Assets Manager | Browse published | Context menu |
| Assets Manager | File Manager | Edit working file | Context menu |
| File Manager | Material Loader | Create materials | Manual workflow |
| Material Loader | Assets Manager | Publish materials | Export to _publish/ |
| Texture Search | Material Loader | Fix then create | Sequential workflow |

---

## 🎨 User Interface Overview

### 1. File Manager (Always Visible)

**MiniBar - Always on screen:**
```
┌────────────────────────────────────────────────────────┐
│ ⋮⋮ │ 🏷️ Type │ 📁 Dept │ [Current File] │ 📄 ⚡ 💾 ⚙️ │
└────────────────────────────────────────────────────────┘
```
- **Position**: Top-right of Houdini window
- **Size**: Compact (400x40 pixels)
- **Always visible**: Auto-starts with Houdini
- **Quick actions**: New file, Quick menu, Save version, Settings

**Settings Dialog - On demand:**
```
┌───────────────────────────────────────────┐
│  File Manager Settings                    │
├───────────────────────────────────────────┤
│  Project Root: [D:/Projects______] [...]  │
│  Current Project: [MyProject_____▾]       │
│  [Scan Project]                           │
│                                           │
│  Available Types:                         │
│  • _characters (45 files)                 │
│  • _props (23 files)                      │
│  • _environments (12 files)               │
│                                           │
│  Available Departments:                   │
│  • 01_modeling (15 files)                 │
│  • 02_rigging (8 files)                   │
│  • 03_lighting (22 files)                 │
└───────────────────────────────────────────┘
```

### 2. Assets Manager (On Demand)

**Main Browser - Opens when needed:**
```
┌─────────────────────────────────────────────────────────────┐
│  Assets Manager                                   [_][□][X]  │
├─────────────────────────────────────────────────────────────┤
│ 🔍 [Search____] Type:[All▾] Format:[USD▾] Date:[All▾]      │
│ 📁 Path: D:/Projects/MyProject/01_assets/_characters/       │
├────────────────────────────┬────────────────────────────────┤
│                            │                                │
│   GRID VIEW                │    PREVIEW PANEL               │
│                            │                                │
│  ┌────┐ ┌────┐ ┌────┐      │    ┌────────────────────┐     │
│  │[#] │ │[#] │ │[#] │      │    │                    │     │
│  │img │ │img │ │img │      │    │   Large Thumbnail  │     │
│  └────┘ └────┘ └────┘      │    │                    │     │
│  Hero    Chair   Tree       │    └────────────────────┘     │
│  v003    v002    v001       │                               │
│                            │    Name: char_hero            │
│  ┌────┐ ┌────┐ ┌────┐      │    Type: _characters          │
│  │[#] │ │[#] │ │[#] │      │    Format: USD                │
│  └────┘ └────┘ └────┘      │    Size: 45.2 MB              │
│  Rock    Lamp   Sword       │    Version: v003              │
│  v001    v003   v002       │    Modified: 2025-01-09       │
│                            │                               │
│  [Grid][List][Refresh]     │    Tags: [hero][character]    │
│                            │                               │
│                            │    [Import][Reference][Copy]  │
├────────────────────────────┴────────────────────────────────┤
│ 📊 234 assets | 12 filtered | Selected: char_hero_v003.usd │
└─────────────────────────────────────────────────────────────┘
```
- **Size**: Large (1024x768+ pixels)
- **Opens**: On demand (menu/shelf/shortcut)
- **Rich UI**: Thumbnails, metadata, filters
- **Heavy features**: Database, cache, thumbnails

### 3. Material Loader (On Demand)

**Simple Dialog:**
```
┌─────────────────────────────────────────────┐
│  Mono Material Loader                       │
├─────────────────────────────────────────────┤
│  Texture Folder:                            │
│  [D:/textures/char_hero/________] [Browse]  │
│                                             │
│  Material Library:                          │
│  [/mat_________________________] [Browse]  │
│                                             │
│  Renderer:                                  │
│  ◉ Redshift  ○ Karma                        │
│                                             │
│  Options:                                   │
│  ☑ Enable UDIM                              │
│  ☑ Auto-connect to geometry                 │
│                                             │
│  [Create Materials]           [Close]       │
└─────────────────────────────────────────────┘
```
- **Size**: Small (400x300 pixels)
- **Simple**: Minimal UI, clear workflow
- **Fast**: Instant material creation

### 4. Texture Search & Replace (On Demand)

**Search Dialog:**
```
┌─────────────────────────────────────────────┐
│  Texture Search & Replace                   │
├─────────────────────────────────────────────┤
│  Search Pattern:                            │
│  [old_path/textures/_________]              │
│  ☑ Use Regex  ☑ Case sensitive             │
│                                             │
│  Replace With:                              │
│  [new_path/textures/_________]              │
│                                             │
│  Scope:                                     │
│  ◉ Selected nodes  ○ All nodes              │
│                                             │
│  Preview:                                   │
│  ┌─────────────────────────────────────┐   │
│  │ /old_path/tex.png → /new_path/tex.png│  │
│  │ /old_path/tex2.png → /new_path/...  │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  Found: 24 textures                         │
│                                             │
│  [Preview]  [Replace All]  [Close]          │
└─────────────────────────────────────────────┘
```
- **Size**: Medium (500x400 pixels)
- **Power user**: Regex support
- **Safe**: Preview before replace

---

## 🔄 Data Flow & Integration

### Integration Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Shared Layer                           │
│  ┌────────────┬─────────────┬────────────────────────┐   │
│  │ QSettings  │ Houdini API │ PySide6 Qt Framework   │   │
│  └────────────┴─────────────┴────────────────────────┘   │
│   • Project settings                                     │
│   • Recent projects                                      │
│   • UI preferences                                       │
└──────────────────────────────────────────────────────────┘
                         ▲
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼─────┐    ┌────▼─────┐    ┌────▼─────┐
   │   File   │    │  Assets  │    │Material  │
   │  Manager │◄──►│  Manager │◄──►│  Loader  │
   └──────────┘    └──────────┘    └──────────┘
        │                │                │
        └────────────────┼────────────────┘
                         ▼
              ┌──────────────────┐
              │  Houdini Scene   │
              │  • Nodes         │
              │  • Parameters    │
              │  • Files         │
              └──────────────────┘
```

### Shared Data

**QSettings (Mono Organization):**
```python
# All tools share these settings
ORG = "Mono"

# File Manager
QSettings(ORG, "FileManager")
- project_root
- current_project
- recent_projects
- minibar_position
- minibar_locked
- minibar_ui_scale

# Assets Manager (reads from FileManager)
QSettings(ORG, "AssetsManager")
- project_root (read from FileManager)
- current_project (read from FileManager)
- thumbnail_size
- view_mode (grid/list)
- filter_presets
- recent_assets

# Material Loader
QSettings(ORG, "MaterialLoader")
- last_texture_folder
- last_material_library
- default_renderer
- udim_enabled

# Texture Search
QSettings(ORG, "TextureSearch")
- recent_search_patterns
- recent_replace_patterns
- regex_enabled
```

### Cross-Tool Workflows

**Workflow 1: Complete Asset Pipeline**
```
[File Manager] Create asset file
      ↓
[Houdini] Model/Rig/Surface asset
      ↓
[Material Loader] Create materials from textures
      ↓
[File Manager] Export to _publish/
      ↓
[Assets Manager] Browse & import published asset
      ↓
[Houdini] Use in production scene
      ↓
[File Manager] Save shot file
```

**Workflow 2: Fix Broken Paths, Then Publish**
```
[File Manager] Open old file
      ↓
[Texture Search] Find broken texture paths
      ↓
[Texture Search] Replace with new paths
      ↓
[Material Loader] Re-create materials
      ↓
[File Manager] Save updated file
      ↓
[File Manager] Export to _publish/
      ↓
[Assets Manager] Verify published asset
```

**Workflow 3: Lighting Scene Setup**
```
[File Manager] Create shot file (Sh010_lighting_v001.hip)
      ↓
[Assets Manager] Browse environments
      ↓
[Assets Manager] Multi-select & import (USD reference)
      ↓
[Assets Manager] Browse props
      ↓
[Assets Manager] Import additional props
      ↓
[Houdini] Layout scene
      ↓
[File Manager] Save version (💾 button in MiniBar)
```

---

## 🚀 Access Methods

### 4-Level Access Pattern

Every tool follows the same access pattern for consistency:

**Level 1: Python API (Programmatic)**
```python
# File Manager
from mono_tools.file_manager import show_mono_file_manager, show_mono_minibar
show_mono_minibar()  # MiniBar
show_mono_file_manager()  # Settings dialog

# Assets Manager
from mono_tools.assets_manager import show_mono_assets_manager, import_asset
show_mono_assets_manager()  # Browser
import_asset("/path/to/asset.usd", mode="usd_reference")

# Material Loader
from mono_tools.material_loader import show_material_loader
show_material_loader()

# Texture Search
from mono_tools.texture_search_replace import show_texture_search_replace
show_texture_search_replace()
```

**Level 2: Houdini Menu**
```
Main Menu → Mono Studio
├─ File Manager
│  ├─ Show MiniBar
│  └─ Settings
├─ Assets Manager
│  └─ Browse Assets
├─ Material Loader
│  └─ Create Materials
└─ Texture Search & Replace
   └─ Search & Replace
```

**Level 3: Shelf Tools**
```
MonoStudio Shelf
┌────┬────┬────┬────┐
│File│Asts│Matl│Tex │
│Mgr │Mgr │Load│Srch│
└────┴────┴────┴────┘
```

**Level 4: Context Menus**
```
Network Editor → Right-click
├─ Import Asset from Manager  (Assets Manager)
└─ Open File Manager

File Manager → Right-click
├─ Browse Published Assets  (Assets Manager)
└─ Create Materials  (Material Loader)

Assets Manager → Right-click
├─ Edit Working File  (File Manager)
└─ Search Textures  (Texture Search)
```

---

## 📈 Performance Characteristics

### Tool Performance Profiles

| Tool | Startup Time | Memory Usage | Disk Usage | CPU Usage |
|------|--------------|--------------|------------|-----------|
| **File Manager (MiniBar)** | < 100ms | 10-20 MB | None | Minimal |
| **File Manager (Settings)** | < 500ms | 30-50 MB | 1 MB (settings) | Low |
| **Assets Manager** | 1-5s (first time) | 100-500 MB | 50-500 MB (cache) | Medium-High |
| **Material Loader** | < 200ms | 20-40 MB | None | Low |
| **Texture Search** | < 300ms | 30-60 MB | None | Low |

### Optimization Strategies

**File Manager:**
- No database (uses QSettings)
- Fast file scanning (only .hip files)
- Minimal UI (MiniBar)
- No thumbnails
- Result: ⚡ Instant startup

**Assets Manager:**
- SQLite database (indexed queries)
- Thumbnail cache (disk + memory)
- Lazy loading (visible items only)
- Background threads (scanning, thumbnails)
- Result: 🐢 Slower but feature-rich

**Material Loader:**
- No caching needed
- Direct Houdini API calls
- Simple texture detection
- Result: ⚡ Fast material creation

**Texture Search:**
- In-memory node traversal
- Regex compilation once
- No caching needed
- Result: ⚡ Fast search/replace

---

## 🎯 When to Use Which Tool?

### Decision Tree

```
Need to work on files?
├─ Yes: Are they scene files (.hip)?
│  ├─ Yes → File Manager
│  └─ No → Continue
└─ No: Are they published assets (USD/FBX)?
   ├─ Yes → Assets Manager
   └─ No: Are they textures?
      ├─ Yes: Need to create materials?
      │  ├─ Yes → Material Loader
      │  └─ No: Need to fix paths?
      │     ├─ Yes → Texture Search
      │     └─ No → Manual workflow
      └─ No: Use standard Houdini tools
```

### Quick Reference

**"I want to..."**

| Goal | Tool | Why |
|------|------|-----|
| Open today's shot file | File Manager (MiniBar) | Quick file switching |
| Save a new version | File Manager (MiniBar) | Version management |
| Find published hero character | Assets Manager | Browse published assets |
| Import environment into scene | Assets Manager | Import/Reference assets |
| Create materials from textures | Material Loader | Auto-material creation |
| Fix broken texture paths | Texture Search | Regex-based path replacement |
| Switch between departments | File Manager (MiniBar) | Department filtering |
| Preview asset before import | Assets Manager | Thumbnail preview |
| See all versions of asset | Assets Manager | Version browsing |
| Setup new shot with assets | Assets Manager + File Manager | Import then save |

---

## 🔮 Future Roadmap

### Planned Features (Priority Order)

**Phase 1: Assets Manager Implementation** (12 weeks)
- Complete Assets Manager v1.0
- Integration with File Manager
- Production testing
- Documentation

**Phase 2: Enhanced Integration** (4 weeks)
- Cross-tool context menus refined
- Unified settings panel
- Shared recent items
- Better workflow automation

**Phase 3: Advanced Features** (8 weeks)
- Assets Manager MiniBar (lightweight version)
- File system watchers (auto-refresh)
- Version comparison tools
- Dependency tracking

**Phase 4: Team Features** (Future)
- Cloud sync (shared tags, ratings)
- Asset analytics (usage tracking)
- Team collaboration (comments, approvals)
- Shotgun/Ftrack integration

**Phase 5: AI Features** (Future)
- Auto-tagging assets (ML-based)
- Smart asset recommendations
- Duplicate detection
- Quality checks (polycount, topology)

---

## 📚 Documentation Index

### User Guides
- **File Manager**: `python/mono_tools/file_manager/README.md`
- **Assets Manager**: `docs/Assets_Manager_Summary.md` (quick reference)
- **Material Loader**: Documentation in tool (tooltips)
- **Texture Search**: `docs/Texture_Search_Replace_Guide.md`

### Technical Documentation
- **General**: `instructions.md` (main development guide)
- **Assets Manager Plan**: `docs/Assets_Manager_Plan.md` (full design)
- **Assets Manager Workflow**: `docs/Assets_Manager_Workflow.md` (integration)
- **Ecosystem**: This file

### Setup & Configuration
- **Installation**: `README.md`
- **Startup**: `docs/Simplified_Startup_Guide.md`
- **Shelf Setup**: `docs/SHELF_SETUP_GUIDE.md`
- **Version Update**: `VERSION_UPDATE_CHECKLIST.md`

---

## 🎓 Learning Path

### For New Users

**Day 1: File Manager Basics**
1. Open Houdini → MiniBar appears automatically
2. Click ⚙️ to configure project
3. Browse files with Type/Dept buttons
4. Open a file
5. Save version with 💾 button

**Day 2: Material Loader**
1. Prepare textures in folder
2. Menu → Mono Studio → Material Loader
3. Select texture folder
4. Choose renderer (Redshift/Karma)
5. Click "Create Materials"
6. Materials appear in /mat

**Day 3: Texture Search (if needed)**
1. Open scene with broken textures
2. Menu → Mono Studio → Texture Search
3. Enter old path pattern
4. Enter new path
5. Preview changes
6. Replace all

**Day 4: Assets Manager (when available)**
1. Open Assets Manager
2. Browse published assets
3. Preview thumbnails and metadata
4. Import asset to scene
5. Continue working

### For TDs

**Week 1: Setup & Configuration**
- Install MonoStudio package
- Configure project structure
- Test all tools
- Setup shelves and menus

**Week 2: Workflow Design**
- Design asset publishing workflow
- Setup _publish/ directory structure
- Create metadata templates
- Test full pipeline

**Week 3: Team Training**
- Train artists on File Manager
- Train artists on Material Loader
- Document studio-specific workflows
- Gather feedback

**Week 4+: Optimization**
- Monitor performance
- Optimize database (Assets Manager)
- Customize for studio needs
- Extend with custom tools

---

## ✅ Success Metrics

### Adoption Metrics
- **Target**: 80%+ of team uses tools daily
- **Measure**: Usage tracking (optional analytics)
- **Timeline**: 3 months post-deployment

### Efficiency Metrics
- **Time to find asset**: < 30 seconds (vs 2-5 minutes manual)
- **Time to create materials**: < 10 seconds (vs 2-3 minutes manual)
- **Time to save version**: < 5 seconds (1 click)

### Quality Metrics
- **Broken texture paths**: < 5% (down from 20-30%)
- **Version conflicts**: < 1% (down from 10-15%)
- **Lost work**: 0% (automatic versioning)

---

## 💬 Team Feedback

### What Users Say (Target Feedback)

**Artists:**
> "MiniBar is always there when I need it. Quick file switching is a game changer."

> "Material Loader saves me 30 minutes per asset. Just point and click!"

> "Assets Manager makes finding published assets so much easier. Love the thumbnails!"

**TDs:**
> "Clean codebase, easy to customize and extend."

> "Good separation of concerns. Each tool does one thing well."

> "Performance is solid even with 1000+ assets."

**Supervisors:**
> "Team productivity increased by 20-30% after adopting MonoStudio."

> "Fewer broken files, better version control, happier artists."

---

**Last Updated**: 2025-01-10  
**Version**: 2.2.0  
**Status**: 3 tools production, 1 in planning  
**Next**: Assets Manager implementation (Phase 1)


