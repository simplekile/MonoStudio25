# Mono File Manager

**Professional scene file management for Houdini**

## Purpose

The File Manager is designed specifically for managing **working scene files** (.hip, .hiplc, .hipnc). It provides quick access to your Houdini scenes across different asset types and shot departments.

## Features

### MiniBar
- **Quick file switching** - Switch between scene files without opening full dialogs
- **Type-based navigation** - Browse by asset type (_characters, _props, etc.) or shots
- **Department filtering** - Filter files by department (modeling, rigging, lighting, etc.)
- **Version tracking** - See current version and switch between versions
- **Quick actions** - Save version, reload scene, open file location

### Settings Dialog
- **Project configuration** - Set project root and current project
- **Dynamic scanning** - Auto-detect asset types and departments
- **File preview** - Table view with file details
- **Statistics** - Show file counts and department info

## Scope

### ✅ Handles:
- Working scene files (.hip, .hiplc, .hipnc)
- Version management and incrementing
- Scene file switching
- Department-based organization

### ❌ Does NOT handle:
- Published assets (FBX, USD, ABC, etc.)
- Texture files
- Cache sequences
- Asset thumbnails
- Asset import/reference

## Separation of Concerns

**File Manager** (This Tool):
- Focus: Daily scene file management
- Files: .hip, .hiplc, .hipnc only
- Location: Working directories (not _publish/)
- Speed: Fast scanning, lightweight UI

**Asset Manager** (Separate Tool - Future):
- Focus: Published asset browsing
- Files: All formats (FBX, USD, ABC, textures, etc.)
- Location: _publish/ directories
- Features: Thumbnails, import/reference, metadata

## Structure

```
01_assets/
├── _characters/              ← Type (tab in MiniBar)
│   ├── char_hero/           ← Asset name
│   │   ├── 01_modeling/     ← Department (filter in Settings)
│   │   │   ├── char_hero_modeling_v001.hip  ✅ Shown in File Manager
│   │   │   ├── char_hero_modeling_v002.hip  ✅ Shown in File Manager
│   │   │   └── _publish/
│   │   │       └── char_hero.fbx            ❌ NOT shown (use Asset Manager)
│   │   └── 02_rigging/
│   │       └── char_hero_rigging_v001.hip   ✅ Shown in File Manager

02_shots/
├── 03_lighting/             ← Department (tab in MiniBar)
│   ├── Sh001_lighting_v005.hip  ✅ Shown in File Manager
│   ├── Sh002_lighting_v003.hip  ✅ Shown in File Manager
│   └── _publish/
│       └── Sh001_lighting.usd   ❌ NOT shown (use Asset Manager)
```

## Usage

### From MiniBar:
1. Select type (_characters, _props, or Shots)
2. Select department (if needed)
3. Click file display to see available files
4. Select file to open in Houdini

### From Settings Dialog:
1. Set project root and current project
2. Click Scan to detect types and departments
3. Browse files in table view
4. Double-click to open file in Houdini

## API

```python
from mono_tools.file_manager import show_mono_minibar, show_mono_file_manager

# Show minibar
minibar = show_mono_minibar()

# Show settings dialog
dialog = show_mono_file_manager()
```

## Performance

**Optimized for speed:**
- Only scans .hip files (ignores other formats)
- No thumbnail loading
- Fast directory scanning
- Lightweight table view
- Minimal memory usage

**Expected performance:**
- < 100 files: Instant scan
- 100-500 files: < 1 second
- 500-1000 files: 1-2 seconds
- > 1000 files: May need additional filtering

## Version History

### v2.1.0 (Current) - Simplified
- Removed publish mode toggle
- Removed asset browsing (moved to Asset Manager)
- Removed thumbnail support
- Focus on working files only
- Improved performance

### v2.0.0 - Dynamic Scanning
- Dynamic type and department scanning
- Settings dialog with tabs
- Publish mode support
- Thumbnail previews

### v1.0.0 - Initial Release
- Basic file listing
- Static tabs
- Manual configuration

## Future Development

The following features have been moved to the planned **Asset Manager** tool:
- Thumbnail grid view
- Published asset browsing
- Multi-format file support
- Import/Reference functionality
- Asset metadata display
- Advanced filtering
- Asset dependencies

## Technical Details

### File Scanning:
- **Assets**: 4 levels (`01_assets/type/asset_name/department/files`)
- **Shots**: 2 levels (`02_shots/department/files`)
- **Ignored folders**: `backup`, `Vers`, `old`, `.git`, `__pycache__`, `_thumbnail`, `_publish`

### Supported Extensions:
- `.hip` - Houdini scene file
- `.hiplc` - Houdini Indie/Limited Commercial
- `.hipnc` - Houdini Non-Commercial

### Settings Storage:
- QSettings (Mono/FileManager)
- Project root and current project
- Type and department selections
- MiniBar position and lock state

## Support

For issues or feature requests related to:
- **Working scene files** → Use File Manager
- **Published assets** → Wait for Asset Manager tool
- **General questions** → Check instructions.md

---

**Last Updated**: 2025-01-09  
**Version**: 2.1.0  
**Status**: Production Ready
