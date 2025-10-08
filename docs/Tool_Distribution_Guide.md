# Mono Studio - Tool Distribution Guide

## 🎯 **Tổng quan phân bổ Tool**

Các tool trong Mono Studio được phân bổ theo **4 cấp độ truy cập** để đảm bảo tính linh hoạt và dễ sử dụng.

## 📋 **Cấu trúc phân bổ**

### 🏗️ **1. Cấp độ File System**
```
python/mono_tools/
├── [tool_name].py                    # Main tool implementation
├── [tool_name]_menu_integration.py   # Menu/shelf integration
├── utils.py                          # Shared utilities
├── qt.py                            # Qt/PySide6 utilities
└── test_demo/                       # Test & demo files
    ├── test_[tool_name].py
    ├── demo_[tool_name].py
    └── verify_[tool_name].py
```

### 🎯 **2. Cấp độ Package (Python Import)**
```python
# Main tools
from mono_tools import show_texture_search_replace
from mono_tools import show_material_loader
from mono_tools import show_mono_file_manager

# Test functions
from mono_tools import test_pyside6
from mono_tools import verify_pyside6
from mono_tools import demo_texture_search_replace
```

### 🍽️ **3. Cấp độ Menu (Houdini Menu Bar)**
```
Menu Bar > Mono Studio
├── Texture Search & Replace
├── Material Loader
├── File Manager
├── ─────────────────────
└── [Future tools...]
```

### 🛠️ **4. Cấp độ Shelf (Houdini Shelf)**
```
Shelf Tab: "Mono Studio"
├── Texture Search & Replace    [🔍]
├── Material Loader            [🎨]
├── File Manager               [📁]
└── [Future tools...]          [⚡]
```

## 🔧 **Chi tiết phân bổ theo Tool**

### 🎨 **Texture Search & Replace**

#### **File Distribution:**
```
python/mono_tools/
├── texture_search_replace.py           # Main tool (GUI + Logic)
├── texture_menu_integration.py         # Menu/shelf integration
└── test_demo/
    ├── test_texture_search_replace.py  # Unit tests
    ├── demo_texture_search_replace.py  # Demo with examples
    └── quick_test_texture.py           # Quick test
```

#### **Access Methods:**
1. **Menu**: `Mono Studio > Texture Search & Replace`
2. **Shelf**: `Mono Studio shelf > Texture Search & Replace`
3. **Python**: `from mono_tools import show_texture_search_replace`
4. **Script**: `exec(open("python/mono_tools/test_demo/demo_texture_search_replace.py").read())`

#### **Integration Points:**
- **Menu**: `texture_menu_integration.py` → `add_texture_tools_to_menu()`
- **Shelf**: `texture_menu_integration.py` → `add_to_shelf()`
- **Package**: `__init__.py` → `show_texture_search_replace`

### 📁 **File Manager**

#### **File Distribution:**
```
python/mono_tools/
├── file_manager.py                     # Main tool
├── file_manager_api.py                 # API wrapper
├── fm_helpers.py                       # Helper functions
├── fm_models.py                        # Data models
├── fm_minibar.py                       # MiniBar component
└── test_demo/
    ├── test_file_manager.py            # Unit tests
    └── demo_file_manager.py            # Demo
```

#### **Access Methods:**
1. **Menu**: `Mono Studio > File Manager`
2. **Shelf**: `Mono Studio shelf > File Manager`
3. **Python**: `from mono_tools import show_mono_file_manager`
4. **MiniBar**: Auto-loaded on startup

### 🎨 **Material Loader**

#### **File Distribution:**
```
python/mono_tools/
├── material_loader.py                  # Main tool
└── test_demo/
    ├── test_material_loader.py         # Unit tests
    └── demo_material_loader.py         # Demo
```

#### **Access Methods:**
1. **Menu**: `Mono Studio > Material Loader`
2. **Shelf**: `Mono Studio shelf > Material Loader`
3. **Python**: `from mono_tools import show_material_loader`

## 🚀 **Quy trình thêm Tool mới**

### **Bước 1: Tạo Tool Files**
```python
# 1. Main tool file
python/mono_tools/new_tool.py

# 2. Menu/shelf integration
python/mono_tools/new_tool_menu_integration.py

# 3. Test files
python/mono_tools/test_demo/test_new_tool.py
python/mono_tools/test_demo/demo_new_tool.py
```

### **Bước 2: Cập nhật Package Exports**
```python
# python/mono_tools/__init__.py
from .new_tool import show_new_tool
from .new_tool_menu_integration import setup_new_tool

__all__ = [
    # ... existing exports
    'show_new_tool',
    'setup_new_tool'
]
```

### **Bước 3: Cập nhật Menu Integration**
```python
# python/mono_tools/new_tool_menu_integration.py
def add_new_tool_to_menu():
    main_menu = hou.menuBar()
    mono_menu = main_menu.addMenu("Mono Studio")
    action = mono_menu.addAction("New Tool")
    action.triggered.connect(show_new_tool)

def add_new_tool_to_shelf():
    shelf = hou.shelves.shelves().get("Mono Studio")
    shelf.addTool(
        name="New Tool",
        script="from mono_tools import show_new_tool; show_new_tool()",
        icon="MISC_tool",
        help_text="Description of new tool"
    )
```

### **Bước 4: Cập nhật Auto-load**
```python
# python/startup/auto_load.py
from mono_tools.new_tool_menu_integration import setup_new_tool

def auto_load_mono_studio():
    # ... existing code
    setup_new_tool()  # Add this line
```

## 📊 **Tool Categories & Organization**

### **🎯 Core Tools** (Essential)
- **File Manager** - File management & navigation
- **Material Loader** - Material creation & loading
- **Texture Search & Replace** - Texture path management

### **🔧 Utility Tools** (Supporting)
- **Qt Utilities** - PySide6 helpers
- **General Utils** - Common functions

### **🧪 Test & Demo Tools** (Development)
- **Test Scripts** - Unit testing
- **Demo Scripts** - User examples
- **Verification Scripts** - System checks

## 🎨 **UI/UX Distribution Strategy**

### **Menu Organization**
```
Mono Studio Menu
├── 🎨 Material Tools
│   ├── Material Loader
│   └── Texture Search & Replace
├── 📁 File Tools
│   ├── File Manager
│   └── File Browser
├── ─────────────────────
├── 🔧 Utilities
│   ├── System Info
│   └── Settings
└── 🧪 Development
    ├── Test Suite
    └── Debug Tools
```

### **Shelf Organization**
```
Mono Studio Shelf
├── [🎨] Material Loader
├── [🔍] Texture Search & Replace
├── [📁] File Manager
├── [⚡] Quick Tools
└── [🔧] Utilities
```

## 🔄 **Auto-loading Strategy**

### **Startup Sequence**
1. **Load Core Modules** - Essential tools first
2. **Setup Menu Integration** - Add to menu bar
3. **Setup Shelf Integration** - Add to shelf
4. **Initialize MiniBar** - Show main interface
5. **Load Optional Tools** - Secondary tools

### **Lazy Loading**
- **Heavy Tools** - Load only when accessed
- **Test Tools** - Load only in development mode
- **Demo Tools** - Load only when needed

## 📈 **Scalability Considerations**

### **Tool Growth Strategy**
- **Modular Design** - Each tool is independent
- **Shared Utilities** - Common functions in utils.py
- **Consistent Interface** - Same access patterns
- **Easy Integration** - Standard integration process

### **Performance Optimization**
- **Lazy Loading** - Load tools on demand
- **Caching** - Cache frequently used data
- **Memory Management** - Clean up unused tools
- **Error Handling** - Graceful degradation

## 🎯 **Best Practices**

### **1. Tool Design**
- **Single Responsibility** - One tool, one purpose
- **Consistent Interface** - Same access methods
- **Error Handling** - Graceful failure
- **Documentation** - Clear usage instructions

### **2. Integration**
- **Menu First** - Always add to menu
- **Shelf Second** - Add to shelf for quick access
- **Python Third** - Ensure Python API works
- **Test Last** - Comprehensive testing

### **3. User Experience**
- **Discoverable** - Easy to find tools
- **Consistent** - Same behavior across tools
- **Efficient** - Quick access to common tools
- **Reliable** - Stable and predictable

## 📚 **Documentation Strategy**

### **Per-Tool Documentation**
```
docs/
├── [Tool_Name]_Guide.md           # User guide
├── [Tool_Name]_API.md             # API reference
├── [Tool_Name]_Troubleshooting.md # Common issues
└── [Tool_Name]_Examples.md        # Usage examples
```

### **System Documentation**
```
docs/
├── Tool_Distribution_Guide.md     # This file
├── API_Reference.md               # Complete API
├── Troubleshooting.md             # System issues
└── README.md                      # Overview
```

---

**Last Updated**: 2024-10-08  
**Version**: 2.0.0  
**Compatibility**: Houdini 21+ (PySide6)
