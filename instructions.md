# Mono Studio - AI Development Instructions

## 🎯 **CRITICAL: Always Use PySide6 for Houdini 21+**

### ⚠️ **MANDATORY REQUIREMENTS**

1. **NEVER use PySide2** - Houdini 21+ requires PySide6
2. **ALWAYS import from PySide6** - `from PySide6 import QtCore, QtGui, QtWidgets`
3. **Check Houdini version** - Ensure compatibility with Houdini 21+
4. **Use relative imports** - `from .module_name import function` for internal modules

### 📋 **Standard Import Pattern (v2.0.0)**

```python
# ✅ CORRECT - Always use this pattern
from PySide6 import QtCore, QtGui, QtWidgets
import hou
import os
import re
from datetime import datetime

# ✅ CORRECT - Relative imports for internal modules
from .texture_search_replace import show_texture_search_replace
from .file_manager import show_mono_file_manager, show_mono_minibar
from .material_loader import show_material_loader
from .qt import QtCore, QtGui, QtWidgets
from .utils import MonoUtils
```

### ❌ **NEVER DO THIS**

```python
# ❌ WRONG - PySide2 is deprecated for Houdini 21+
from PySide2 import QtCore, QtGui, QtWidgets

# ❌ WRONG - Absolute imports for internal modules
from texture_search_replace import show_texture_search_replace
```

### 🏗️ **Project Structure**

```
python/
├── mono_tools/
│   ├── __init__.py                 # Main package exports
│   ├── qt.py                      # PySide6 wrapper
│   ├── texture_search_replace.py  # Main tools
│   ├── texture_menu_integration.py
│   ├── file_manager.py
│   ├── material_loader.py
│   ├── utils.py
│   └── test_demo/                 # Test and demo files
│       ├── test_pyside6.py
│       ├── verify_pyside6.py
│       ├── test_texture_search_replace.py
│       ├── demo_texture_search_replace.py
│       └── quick_test_pyside6.py
├── startup/
│   └── auto_load.py
└── Mono_MaterialLoader.py
```

### 📁 **Folder Classification Guidelines**

#### 🎯 **Main Package Structure (CURRENT v2.0.0)**
```
python/
├── mono_tools/                    # Main package (5 tool folders)
│   ├── __init__.py               # Package exports & initialization (v2.0.0)
│   ├── file_manager/             # File management tool (complete)
│   │   ├── file_manager.py       # Main tool
│   │   ├── file_manager_api.py   # API wrapper
│   │   ├── file_manager_helpers.py # Helper functions
│   │   ├── file_manager_manager.py # Manager class
│   │   ├── file_manager_minibar.py # MiniBar component
│   │   ├── file_manager_models.py # Data models
│   │   └── file_manager_menu_integration.py # Menu integration
│   ├── material_loader/          # Material loading tool (complete)
│   │   ├── material_loader.py    # Main tool
│   │   └── material_loader_menu_integration.py # Menu integration
│   ├── texture_search_replace/   # Texture search & replace tool (complete)
│   │   ├── texture_search_replace.py # Main tool
│   │   └── texture_menu_integration.py # Menu integration
│   ├── qt/                       # Qt/PySide6 utilities (complete)
│   │   └── qt.py                 # PySide6 wrapper
│   ├── utils/                    # General utilities (complete)
│   │   └── utils.py              # Utility functions
│   └── test_demo/                # Test & demo scripts (complete)
│       ├── test_pyside6.py       # PySide6 tests
│       ├── verify_pyside6.py     # Verification scripts
│       ├── demo_texture_search_replace.py # Demo scripts
│       └── [other test files]    # Additional tests
├── analysis/                     # Analysis tools (complete)
│   ├── analyze_current_structure.py
│   ├── analyze_tool_structure.py
│   ├── analyze_remaining_files.py
│   └── simple_analyze.py
├── migration/                    # Migration tools (complete)
│   ├── migrate_all_tools_to_folders.py
│   ├── backup_before_migration.py
│   └── simple_migration_test.py
├── testing/                      # Testing tools (complete)
│   ├── check_tool_consistency.py
│   ├── simple_consistency_check.py
│   ├── test_after_migration.py
│   ├── test_texture_fix_simple.py # Simple texture fix test
│   ├── test_texture_fix.py        # Texture fix test
│   └── [other test files]
├── utilities/                    # Legacy/utility files (complete)
│   ├── Mono_MaterialLoader.py    # Legacy material loader
│   ├── mono_startup.py           # Startup utilities
│   ├── create_shelf_correct.py   # Shelf creation utilities
│   ├── create_shelf_in_houdini.py # Houdini shelf creation
│   ├── create_shelf.py           # General shelf creation
│   ├── debug_shelf_api.py        # Shelf API debugging
│   ├── setup_shelf.py            # Shelf setup utilities
│   ├── query_houdini_icons.py    # Houdini icons query
│   └── uiready.py                # UI readiness utilities
├── startup/                      # Houdini startup scripts (complete)
│   ├── auto_load.py              # Auto-loading
│   └── 123.py                    # Additional startup
└── docs/                         # Documentation (6 files)
    ├── No_Install_Report.md
    ├── Project_Cleanup_Report.md
    ├── Texture_Search_Replace_Guide.md
    ├── Tool_Distribution_Guide.md
    ├── HOUDINI_ICONS_GUIDE.md     # Houdini icons guide
    └── SHELF_SETUP_GUIDE.md       # Shelf setup guide
```

#### 📂 **Folder Naming Conventions (UPDATED)**

##### **Main Package** (`mono_tools/`)
- **Each tool has its own folder**
- **Structure**: `[tool_name]/[tool_name].py` + helpers + integration
- **Example**: `file_manager/file_manager.py`, `texture_search_replace/texture_search_replace.py`

##### **Tool Folders** (`mono_tools/[tool_name]/`)
- `[tool_name].py` - Main tool implementation
- `[tool_name]_menu_integration.py` - Menu/shelf integration
- `[tool_name]_helpers.py` - Helper functions (if needed)
- `[tool_name]_models.py` - Data models (if needed)
- `[tool_name]_api.py` - API wrapper (if needed)
- `__init__.py` - Package exports

##### **Analysis Tools** (`analysis/`) - NEW
- `analyze_[purpose].py` - Analysis scripts
- `simple_[purpose].py` - Simplified analysis scripts
- **Purpose**: Project structure analysis, file categorization

##### **Migration Tools** (`migration/`) - NEW
- `migrate_[purpose].py` - Migration scripts
- `backup_[purpose].py` - Backup scripts
- `test_[purpose].py` - Migration test scripts
- **Purpose**: Project migration, organization, backup

##### **Testing Tools** (`testing/`) - NEW
- `test_[purpose].py` - Test scripts
- `check_[purpose].py` - Consistency check scripts
- `verify_[purpose].py` - Verification scripts
- **Purpose**: Testing, verification, consistency checks

##### **Utilities** (`utilities/`) - NEW
- `[legacy_name].py` - Legacy files
- `[utility_name].py` - Utility scripts
- **Purpose**: Legacy support, utility functions

##### **Test & Demo** (`mono_tools/test_demo/`)
- `test_[feature_name].py` - Unit tests for specific features
- `verify_[feature_name].py` - Verification scripts
- `demo_[feature_name].py` - Demo scripts with examples
- `quick_test_[feature_name].py` - Quick test scripts

##### **Startup** (`startup/`)
- `auto_load.py` - Auto-loading scripts
- `[environment]_startup.py` - Environment-specific startup

##### **Documentation** (`docs/`)
- `[Feature_Name]_Guide.md` - Feature documentation
- `API_Reference.md` - API documentation
- `Troubleshooting.md` - Common issues & solutions

#### 🔧 **File Organization Rules**

##### **1. Tool Files (NEW STRUCTURE)**
```
mono_tools/[tool_name]/
├── __init__.py                           # Package exports
├── [tool_name].py                        # Main tool
├── [tool_name]_menu_integration.py       # Menu integration
├── [tool_name]_helpers.py                # Helper functions (if needed)
├── [tool_name]_models.py                 # Data models (if needed)
└── [tool_name]_api.py                    # API wrapper (if needed)
```

##### **2. Test Files**
```
test_demo/
├── test_texture_search_replace.py    # Unit tests
├── verify_texture_search_replace.py  # Verification
├── demo_texture_search_replace.py    # Demo with examples
└── quick_test_texture.py             # Quick test
```

##### **3. Documentation Files (v2.0.0)**
```
docs/
├── Texture_Search_Replace_Guide.md   # User guide
├── Tool_Distribution_Guide.md        # Tool distribution guide
├── Project_Cleanup_Report.md         # Project cleanup report
└── No_Install_Report.md              # Installation report
```

#### 📋 **File Naming Standards**

##### **Python Files**
- `snake_case.py` - All Python files
- `[feature]_[type].py` - Feature + type (e.g., `texture_menu_integration.py`)
- `test_[feature].py` - Test files
- `demo_[feature].py` - Demo files
- `verify_[feature].py` - Verification files

##### **Documentation Files (v2.0.0)**
- `[Feature_Name]_Guide.md` - User guides
- `[Feature_Name]_Distribution_Guide.md` - Tool distribution guides
- `[Feature_Name]_Report.md` - Project reports
- `[Feature_Name]_Troubleshooting.md` - Troubleshooting guides

##### **Configuration Files**
- `[feature]_config.json` - Configuration files
- `[feature]_settings.py` - Settings modules

#### 🚫 **Auto-Ignore File Patterns (DO NOT CREATE)**

The following file patterns are **automatically ignored** by `.gitignore`. **NEVER create files matching these patterns** unless absolutely necessary:

##### **❌ Shelf Files - Test/Experimental Versions**
```
# These will be auto-ignored:
shelves/*_Test*.shelf          # Test versions
shelves/*_Fixed*.shelf         # Fixed versions (create new version instead)
shelves/*_Alternative*.shelf   # Alternative versions
shelves/*_Real*.shelf          # Test versions
shelves/*_XML*.shelf           # XML test versions
shelves/*_experimental*.shelf  # Experimental versions
shelves/*_backup*.shelf        # Backup versions
shelves/*_old*.shelf           # Old versions

# ✅ Keep only these official shelf files:
shelves/MonoStudio.shelf               # Main shelf
shelves/MonoStudioAdvanced.shelf      # Advanced version
shelves/MonoStudio_Professional.shelf # Professional version (optional)
```

##### **❌ Temporary/Test Python Files**
```
# These will be auto-ignored:
**/quick_test_*.py      # Quick temporary tests
**/temp_*.py            # Temporary files
**/scratch_*.py         # Scratch/test files
**/experiment_*.py      # Experimental files
**/experimental_*.py    # Experimental versions
```

##### **❌ Backup/Old Version Files**
```
# These will be auto-ignored:
**/*_backup.*           # Backup files
**/*_old.*              # Old version files
**/*_v[0-9]*_backup.*   # Version backups
**/*_copy.*             # Copy files
**/*_duplicate.*        # Duplicate files
```

##### **✅ Instead, Use Proper Naming:**
```
# ✅ CORRECT - Use version control or proper naming:
python/mono_tools/file_manager/file_manager.py      # Main file
python/mono_tools/test_demo/test_file_manager.py    # Proper test
docs/File_Manager_Guide.md                          # Documentation

# ❌ WRONG - Will be auto-ignored:
python/temp_file_manager.py                         # Use test_demo/ instead
shelves/MonoStudio_TestIcons.shelf                  # Create new version instead
file_manager_backup.py                              # Use git versioning instead
```

##### **📝 Rule of Thumb:**
1. **Use git** for versioning, not `_backup`, `_old`, `_copy` suffixes
2. **Use test_demo/** for tests, not `quick_test_*`, `temp_*`
3. **Create new shelf versions** only when needed, name them descriptively
4. **Delete experimental files** after testing, don't keep `_experimental` versions

#### 🗂️ **Folder Creation Rules (UPDATED)**

##### **When to Create New Folders**
1. **Main tools** - Always create `[tool_name]/` folder
2. **Analysis tools** - Use `analysis/` for analysis scripts
3. **Migration tools** - Use `migration/` for migration scripts
4. **Testing tools** - Use `testing/` for testing scripts
5. **Utilities** - Use `utilities/` for legacy/utility files
6. **Test organization** - Always use `test_demo/` for tests
7. **Documentation** - Use `docs/` for all documentation

##### **When NOT to Create Folders**
1. **Single utility files** - Use appropriate utility folder
2. **Small features** - Still create folder for consistency
3. **Over-organization** - Don't create too many nested folders

#### 📁 **Example Folder Structure by Feature**

##### **File Manager Feature (Complex Tool)**
```
python/mono_tools/file_manager/
├── __init__.py
├── file_manager.py                     # Main tool
├── file_manager_api.py                 # API wrapper
├── file_manager_helpers.py             # Helper functions
├── file_manager_manager.py             # Manager class
├── file_manager_minibar.py             # MiniBar component
├── file_manager_models.py              # Data models
└── file_manager_menu_integration.py    # Menu integration

python/mono_tools/test_demo/
├── test_file_manager.py                # Unit tests
└── demo_file_manager.py                # Demo

docs/
└── File_Manager_Guide.md               # Documentation
```

##### **Texture Search & Replace Feature (Simple Tool)**
```
python/mono_tools/texture_search_replace/
├── __init__.py
├── texture_search_replace.py           # Main tool
└── texture_menu_integration.py         # Menu integration

python/mono_tools/test_demo/
├── test_texture_search_replace.py      # Unit tests
└── demo_texture_search_replace.py      # Demo

docs/
└── Texture_Search_Replace_Guide.md     # Documentation
```

##### **Analysis Tools (NEW)**
```
python/analysis/
├── __init__.py
├── analyze_current_structure.py        # Structure analysis
├── analyze_tool_structure.py           # Tool analysis
├── analyze_remaining_files.py          # File analysis
└── simple_analyze.py                   # Simple analysis
```

##### **Migration Tools (NEW)**
```
python/migration/
├── __init__.py
├── migrate_all_tools_to_folders.py     # Migration script
├── backup_before_migration.py          # Backup script
└── simple_migration_test.py            # Migration test
```

#### 🎯 **Best Practices**

##### **1. Keep Related Files Together**
- All tool files in `[tool_name]/` folder
- All tests in `test_demo/`
- All docs in `docs/`
- All utilities in appropriate utility folders

##### **2. Use Descriptive Names**
- `texture_search_replace.py` not `texture.py`
- `test_texture_search_replace.py` not `test.py`
- `Texture_Search_Replace_Guide.md` not `guide.md`

##### **3. Maintain Consistency**
- Same naming pattern across all features
- Same folder structure for similar features
- Same file organization principles

##### **4. Document Structure**
- Update `instructions.md` when adding new patterns
- Document folder purposes in README files
- Keep structure simple and logical

##### **5. Tool Distribution (v2.0.0)**
- Follow 4-level access pattern (File → Package → Menu → Shelf)
- Each tool has consistent access methods
- **File Manager**: Full dialog + MiniBar integration
- **Material Loader**: Redshift/Karma material creation
- **Texture Search & Replace**: Path management with regex support
- Maintain separation between core tools and utilities

##### **6. Tool Consistency**
- Follow naming conventions: `[tool_name].py`, `show_[tool_name]()`
- All tools must have menu integration
- All tools must have shelf integration
- All tools must have Python API
- All tools must have documentation

### 🔧 **Development Guidelines**

#### 1. **New Tool Creation**
- Always inherit from `QtWidgets.QDialog` or `QtWidgets.QWidget`
- Use PySide6 imports exclusively
- Include proper error handling for Houdini environment
- Add to `__init__.py` exports

#### 2. **GUI Components**
```python
class MyTool(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("My Tool")
        self.setMinimumSize(400, 300)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        # Add widgets here
```

#### 3. **Menu Integration**
```python
def add_to_menu():
    main_menu = hou.menuBar()
    # Find or create Mono Studio menu
    mono_menu = main_menu.addMenu("Mono Studio")
    action = mono_menu.addAction("My Tool")
    action.triggered.connect(my_function)
```

#### 4. **Error Handling**
```python
try:
    import hou
    # Houdini-specific code
except ImportError:
    print("⚠️ Not running in Houdini environment")
    return False
```

### 🧪 **Testing Requirements**

#### 1. **Always Test PySide6 Compatibility**
```python
def test_pyside6():
    try:
        from PySide6 import QtCore, QtGui, QtWidgets
        print("✅ PySide6 OK")
        return True
    except ImportError as e:
        print(f"❌ PySide6 failed: {e}")
        return False
```

#### 2. **Test in Houdini Environment**
- Run tests in Houdini Python Console
- Verify menu integration works
- Check widget creation and display

#### 3. **Test Files Location**
- All test files go in `python/mono_tools/test_demo/`
- Use descriptive names: `test_feature_name.py`
- Include demo scripts for user testing

### 📚 **Documentation Standards**

#### 1. **Function Documentation**
```python
def my_function(param1, param2=None):
    """
    Brief description of function.
    
    Args:
        param1 (str): Description of param1
        param2 (bool, optional): Description of param2. Defaults to None.
    
    Returns:
        bool: Success status
    
    Raises:
        ImportError: If Houdini not available
    """
```

#### 2. **Module Documentation**
```python
"""
Module Name - Brief Description
Compatible with Houdini 21+ (PySide6)
"""
```

### 🚀 **Deployment Checklist (v2.0.0)**

- [x] All imports use PySide6
- [x] Relative imports for internal modules
- [x] Error handling for Houdini environment
- [x] **Folder structure follows guidelines**
- [x] **Files named according to conventions**
- [x] **Function naming follows conventions**
- [x] **Menu integration implemented**
- [x] **Shelf integration implemented**
- [x] Test files in `test_demo/` folder
- [x] Documentation in `docs/` folder
- [x] Added to `__init__.py` exports
- [x] **Consistency check passes**
- [x] Documentation updated
- [x] Tested in Houdini 21+
- [x] **MiniBar integration working**
- [x] **All 3 core tools functional**
- [x] **Project cleanup completed**

### 🔍 **Common Issues & Solutions**

#### Issue: ImportError with PySide2
**Solution**: Change all imports to PySide6

#### Issue: Relative import errors
**Solution**: Use `from .module import function` syntax

#### Issue: Widget not displaying
**Solution**: Check if running in Houdini environment, ensure proper parent widget

#### Issue: Menu not appearing
**Solution**: Verify menu integration code and Houdini menu system

#### Issue: Files scattered across folders
**Solution**: Follow folder classification guidelines, use consistent naming

#### Issue: Test files mixed with main code
**Solution**: Move all test files to `test_demo/` folder

#### Issue: Documentation not organized
**Solution**: Use `docs/` folder with descriptive filenames

### 📞 **Support Information**

- **Target Houdini Version**: 21+
- **Qt Version**: PySide6
- **Python Version**: 3.11+ (Houdini 21 default)
- **Platform**: Windows/Linux/macOS
- **Current Status**: Production Ready (v2.0.0)
- **Last Major Update**: December 2024

### 🎉 **Current Project Status (v2.2.0)**

#### **✅ Completed Features:**
- **File Manager**: Complete with MiniBar integration
- **Material Loader**: Redshift/Karma material creation
- **Texture Search & Replace**: Path management with regex
- **Project Cleanup**: 20+ files removed, structure optimized
- **Documentation**: Essential docs, clean structure
- **Testing**: Comprehensive test suite in place
- **Migration**: All tools migrated to folder structure
- **Simplified Startup**: Streamlined initialization (45 lines vs 200+)

#### **✅ Production Ready:**
- All core tools functional
- Menu and shelf integration working
- MiniBar auto-loading on startup
- Clean project structure
- Professional documentation
- Easy installation process

#### **📋 In Planning:**
- **Assets Manager**: Published asset browser (USD, FBX, ABC)
  - See: `docs/Assets_Manager_Plan.md` (full design)
  - See: `docs/Assets_Manager_Workflow.md` (integration patterns)
  - See: `docs/Assets_Manager_Summary.md` (quick reference)
  - Status: Planning phase, ready for implementation
  - Timeline: 12 weeks (6 phases)

#### **📊 Project Statistics:**
- **Total Files**: ~50+ (optimized from 70+)
- **Core Tools**: 3 production, 1 in planning
  - Production: File Manager, Material Loader, Texture Search
  - Planning: Assets Manager
- **Documentation**: 10+ files (user guides, technical docs, plans)
- **Test Files**: 10+ comprehensive tests
- **Shelf Files**: 9 different shelf configurations

### 🎯 **Remember**

1. **PySide6 ONLY** - No exceptions
2. **Test everything** - In Houdini environment
3. **Document properly** - For future maintenance
4. **Use relative imports** - For internal modules
5. **Handle errors gracefully** - Houdini environment checks
6. **Follow folder guidelines** - Consistent organization
7. **Use descriptive names** - Clear file and folder names
8. **Keep structure simple** - Don't over-organize

---

**Last Updated**: 2024-12-19
**Version**: 2.2.0
**Compatibility**: Houdini 21+ (PySide6)
**Status**: Production Ready
