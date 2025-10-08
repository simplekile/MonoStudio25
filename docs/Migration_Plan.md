# Mono Studio - Migration Plan for Tool Consistency

## 🎯 **Mục tiêu: Chuẩn hóa tất cả tools theo quy tắc nhất quán**

### 📊 **Kết quả kiểm tra hiện tại:**
- ✅ **Function Naming**: PASS
- ✅ **Package Exports**: PASS  
- ❌ **File Naming**: FAIL (4 issues)
- ❌ **Menu Integration**: FAIL (6 tools thiếu menu)

## 🚀 **Migration Plan**

### **Phase 1: File Naming Standardization**

#### **1.1 Rename File Manager files**
```bash
# Current → New
fm_helpers.py → file_manager_helpers.py
fm_manager.py → file_manager_manager.py  
fm_minibar.py → file_manager_minibar.py
fm_models.py → file_manager_models.py
```

#### **1.2 Update imports after renaming**
```python
# Update in all files that import these modules
from .file_manager_helpers import parse_ver, increment_version_and_backup
from .file_manager_manager import MonoFileManager
from .file_manager_minibar import show_mono_minibar
from .file_manager_models import FileModel
```

### **Phase 2: Menu Integration**

#### **2.1 Create missing menu integration files**

**File Manager Menu Integration:**
```python
# python/mono_tools/file_manager_menu_integration.py
import hou
from .file_manager import show_mono_file_manager

def add_file_manager_to_menu():
    """Add File Manager to Houdini menu"""
    try:
        main_menu = hou.menuBar()
        mono_menu = main_menu.addMenu("Mono Studio")
        action = mono_menu.addAction("File Manager")
        action.triggered.connect(show_mono_file_manager)
        print("✅ File Manager added to menu")
    except Exception as e:
        print(f"❌ Error adding File Manager to menu: {e}")

def add_file_manager_to_shelf():
    """Add File Manager to Houdini shelf"""
    try:
        shelf = hou.shelves.shelves().get("Mono Studio")
        if not shelf:
            shelf = hou.shelves.shelves().create("Mono Studio")
        
        script = """
import hou
from mono_tools import show_mono_file_manager
show_mono_file_manager()
"""
        
        shelf.addTool(
            name="File Manager",
            script=script,
            icon="MISC_folder",
            help_text="File management and navigation"
        )
        print("✅ File Manager added to shelf")
    except Exception as e:
        print(f"❌ Error adding File Manager to shelf: {e}")

def setup_file_manager_tools():
    """Setup all file manager tools"""
    add_file_manager_to_menu()
    add_file_manager_to_shelf()
```

**Material Loader Menu Integration:**
```python
# python/mono_tools/material_loader_menu_integration.py
import hou
from .material_loader import show_material_loader

def add_material_loader_to_menu():
    """Add Material Loader to Houdini menu"""
    try:
        main_menu = hou.menuBar()
        mono_menu = main_menu.addMenu("Mono Studio")
        action = mono_menu.addAction("Material Loader")
        action.triggered.connect(show_material_loader)
        print("✅ Material Loader added to menu")
    except Exception as e:
        print(f"❌ Error adding Material Loader to menu: {e}")

def add_material_loader_to_shelf():
    """Add Material Loader to Houdini shelf"""
    try:
        shelf = hou.shelves.shelves().get("Mono Studio")
        if not shelf:
            shelf = hou.shelves.shelves().create("Mono Studio")
        
        script = """
import hou
from mono_tools import show_material_loader
show_material_loader()
"""
        
        shelf.addTool(
            name="Material Loader",
            script=script,
            icon="MISC_material",
            help_text="Material creation and loading"
        )
        print("✅ Material Loader added to shelf")
    except Exception as e:
        print(f"❌ Error adding Material Loader to shelf: {e}")

def setup_material_loader_tools():
    """Setup all material loader tools"""
    add_material_loader_to_menu()
    add_material_loader_to_shelf()
```

#### **2.2 Update auto_load.py**
```python
# python/startup/auto_load.py
from mono_tools.file_manager_menu_integration import setup_file_manager_tools
from mono_tools.material_loader_menu_integration import setup_material_loader_tools

def auto_load_mono_studio():
    # ... existing code
    setup_file_manager_tools()
    setup_material_loader_tools()
```

### **Phase 3: Package Structure Optimization**

#### **3.1 Create File Manager folder**
```bash
mkdir python/mono_tools/file_manager
```

#### **3.2 Move files to folder**
```bash
move python/mono_tools/file_manager.py python/mono_tools/file_manager/
move python/mono_tools/file_manager_api.py python/mono_tools/file_manager/
move python/mono_tools/file_manager_helpers.py python/mono_tools/file_manager/
move python/mono_tools/file_manager_manager.py python/mono_tools/file_manager/
move python/mono_tools/file_manager_minibar.py python/mono_tools/file_manager/
move python/mono_tools/file_manager_models.py python/mono_tools/file_manager/
move python/mono_tools/file_manager_menu_integration.py python/mono_tools/file_manager/
```

#### **3.3 Create file_manager/__init__.py**
```python
# python/mono_tools/file_manager/__init__.py
from .file_manager import show_mono_file_manager
from .file_manager_api import FileManagerWrapper
from .file_manager_minibar import show_mono_minibar
from .file_manager_manager import MonoFileManager
from .file_manager_models import FileModel
from .file_manager_helpers import parse_ver, increment_version_and_backup
from .file_manager_menu_integration import setup_file_manager_tools

__all__ = [
    'show_mono_file_manager',
    'FileManagerWrapper',
    'show_mono_minibar',
    'MonoFileManager',
    'FileModel',
    'parse_ver',
    'increment_version_and_backup',
    'setup_file_manager_tools'
]
```

### **Phase 4: Update Main Package**

#### **4.1 Update python/mono_tools/__init__.py**
```python
# python/mono_tools/__init__.py
from .file_manager import show_mono_file_manager, FileManagerWrapper, show_mono_minibar
from .material_loader import show_material_loader
from .material_loader_menu_integration import setup_material_loader_tools
from .texture_search_replace import show_texture_search_replace
from .texture_menu_integration import setup_texture_tools
from .utils import MonoUtils

# Test and verification functions
try:
    from .test_demo.test_pyside6 import run_all_tests as test_pyside6
    from .test_demo.verify_pyside6 import run_verification as verify_pyside6
    from .test_demo.demo_texture_search_replace import run_full_demo as demo_texture_search_replace
except ImportError:
    test_pyside6 = None
    verify_pyside6 = None
    demo_texture_search_replace = None

__all__ = [
    'show_mono_file_manager',
    'FileManagerWrapper', 
    'show_mono_minibar',
    'show_material_loader',
    'setup_material_loader_tools',
    'show_texture_search_replace',
    'setup_texture_tools',
    'MonoUtils',
    'QtCore', 'QtGui', 'QtWidgets', 'QT_API',
    'test_pyside6', 'verify_pyside6', 'demo_texture_search_replace',
    'initialize'
]
```

## 📋 **Migration Checklist**

### **Phase 1: File Naming**
- [ ] Rename fm_*.py files to file_manager_*.py
- [ ] Update all imports in affected files
- [ ] Test functionality after renaming

### **Phase 2: Menu Integration**
- [ ] Create file_manager_menu_integration.py
- [ ] Create material_loader_menu_integration.py
- [ ] Update auto_load.py to include new integrations
- [ ] Test menu and shelf integration

### **Phase 3: Package Structure**
- [ ] Create file_manager/ folder
- [ ] Move files to folder
- [ ] Create file_manager/__init__.py
- [ ] Update main __init__.py imports
- [ ] Test all imports work correctly

### **Phase 4: Final Testing**
- [ ] Run consistency check script
- [ ] Test all tools from menu
- [ ] Test all tools from shelf
- [ ] Test all tools from Python
- [ ] Verify documentation is up to date

## 🎯 **Expected Results After Migration**

### **File Structure:**
```
python/mono_tools/
├── __init__.py
├── qt.py
├── utils.py
├── material_loader.py
├── material_loader_menu_integration.py
├── texture_search_replace.py
├── texture_menu_integration.py
├── file_manager/
│   ├── __init__.py
│   ├── file_manager.py
│   ├── file_manager_api.py
│   ├── file_manager_helpers.py
│   ├── file_manager_manager.py
│   ├── file_manager_minibar.py
│   ├── file_manager_models.py
│   └── file_manager_menu_integration.py
└── test_demo/
    └── [test files]
```

### **Consistency Check Results:**
- ✅ File Naming: PASS
- ✅ Function Naming: PASS
- ✅ Menu Integration: PASS
- ✅ Package Exports: PASS

### **All Tools Accessible From:**
- 🍽️ Menu: Mono Studio > [Tool Name]
- 🛠️ Shelf: Mono Studio shelf > [Tool Icon]
- 🐍 Python: `from mono_tools import show_[tool_name]`
- 📜 Script: `exec(open("script.py").read())`

## ⚠️ **Important Notes**

1. **Backup before migration** - Create backup of current state
2. **Test after each phase** - Don't skip testing steps
3. **Update documentation** - Keep docs in sync with changes
4. **Incremental approach** - Complete one phase before starting next
5. **Rollback plan** - Have plan to revert if issues arise

---

**Goal**: Achieve 100% consistency across all tools with standardized naming, structure, and integration patterns.
