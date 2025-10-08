# Mono Studio - Tool Consistency Rules

## 🎯 **Nguyên tắc nhất quán cho tất cả Tool**

### 📋 **Rule 1: File Naming Convention**

#### **Main Tool Files**
```
[tool_name].py                    # Main tool implementation
[tool_name]_menu_integration.py   # Menu/shelf integration
[tool_name]_helpers.py            # Helper functions (if needed)
[tool_name]_models.py             # Data models (if needed)
```

#### **Examples**
```
✅ CORRECT:
├── texture_search_replace.py
├── texture_menu_integration.py
├── material_loader.py
├── material_menu_integration.py
├── file_manager.py
├── file_manager_menu_integration.py

❌ WRONG:
├── textureSearchReplace.py
├── texture_menu.py
├── material_loader_tool.py
├── fileManager.py
```

### 📁 **Rule 2: Folder Structure**

#### **Single Tool (1-3 files)**
```
python/mono_tools/
├── [tool_name].py
├── [tool_name]_menu_integration.py
└── [tool_name]_helpers.py (optional)
```

#### **Complex Tool (4+ files)**
```
python/mono_tools/
└── [tool_name]/
    ├── __init__.py
    ├── [tool_name].py
    ├── [tool_name]_menu_integration.py
    ├── [tool_name]_helpers.py
    └── [tool_name]_models.py
```

### 🔧 **Rule 3: Function Naming**

#### **Main Functions**
```python
def show_[tool_name]():           # Main dialog function
def create_[tool_name]():         # Create tool instance
def setup_[tool_name]():          # Setup/integration function
```

#### **Examples**
```python
✅ CORRECT:
def show_texture_search_replace():
def show_material_loader():
def show_file_manager():
def setup_texture_tools():
def setup_material_tools():

❌ WRONG:
def textureSearchReplace():
def showMaterialLoader():
def open_file_manager():
```

### 📦 **Rule 4: Package Exports**

#### **Standard Exports Pattern**
```python
# python/mono_tools/__init__.py
from .[tool_name] import show_[tool_name]
from .[tool_name]_menu_integration import setup_[tool_name]_tools

__all__ = [
    # ... existing exports
    'show_[tool_name]',
    'setup_[tool_name]_tools'
]
```

#### **Examples**
```python
# Texture Search & Replace
from .texture_search_replace import show_texture_search_replace
from .texture_menu_integration import setup_texture_tools

# Material Loader  
from .material_loader import show_material_loader
from .material_menu_integration import setup_material_tools

# File Manager
from .file_manager import show_file_manager
from .file_manager_menu_integration import setup_file_manager_tools
```

### 🍽️ **Rule 5: Menu Integration**

#### **Standard Menu Pattern**
```python
def add_[tool_name]_to_menu():
    """Add [Tool Name] to Houdini menu"""
    try:
        main_menu = hou.menuBar()
        
        # Find or create Mono Studio menu
        mono_menu = main_menu.addMenu("Mono Studio")
        
        # Add tool action
        action = mono_menu.addAction("[Tool Display Name]")
        action.triggered.connect(show_[tool_name])
        
        print(f"✅ [Tool Display Name] added to menu")
        
    except Exception as e:
        print(f"❌ Error adding [Tool Display Name] to menu: {e}")
```

#### **Examples**
```python
# Texture Search & Replace
def add_texture_tools_to_menu():
    action = mono_menu.addAction("Texture Search & Replace")
    action.triggered.connect(show_texture_search_replace)

# Material Loader
def add_material_tools_to_menu():
    action = mono_menu.addAction("Material Loader")
    action.triggered.connect(show_material_loader)
```

### 🛠️ **Rule 6: Shelf Integration**

#### **Standard Shelf Pattern**
```python
def add_[tool_name]_to_shelf():
    """Add [Tool Name] to Houdini shelf"""
    try:
        shelf = hou.shelves.shelves().get("Mono Studio")
        if not shelf:
            shelf = hou.shelves.shelves().create("Mono Studio")
        
        script = f"""
import hou
from mono_tools import show_[tool_name]
show_[tool_name]()
"""
        
        shelf.addTool(
            name="[Tool Display Name]",
            script=script,
            icon="[ICON_NAME]",
            help_text="[Tool description]"
        )
        
        print(f"✅ [Tool Display Name] added to shelf")
        
    except Exception as e:
        print(f"❌ Error adding [Tool Display Name] to shelf: {e}")
```

### 🧪 **Rule 7: Test Files**

#### **Test File Naming**
```
test_demo/
├── test_[tool_name].py              # Unit tests
├── demo_[tool_name].py              # Demo script
├── verify_[tool_name].py            # Verification script
└── quick_test_[tool_name].py        # Quick test
```

#### **Test Function Naming**
```python
def test_[tool_name]():               # Main test function
def demo_[tool_name]():               # Demo function
def verify_[tool_name]():             # Verification function
def run_[tool_name]_tests():          # Run all tests
```

### 📚 **Rule 8: Documentation**

#### **Documentation Files**
```
docs/
├── [Tool_Name]_Guide.md             # User guide
├── [Tool_Name]_API.md               # API reference
├── [Tool_Name]_Troubleshooting.md   # Troubleshooting
└── [Tool_Name]_Examples.md          # Usage examples
```

#### **Documentation Structure**
```markdown
# [Tool Name] Guide

## Overview
Brief description of the tool

## Features
- Feature 1
- Feature 2

## Usage
### From Menu
### From Shelf
### From Python

## Examples
### Basic Usage
### Advanced Usage

## Troubleshooting
### Common Issues
### Solutions
```

### 🎨 **Rule 9: GUI Standards**

#### **Dialog Class Naming**
```python
class [ToolName]Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("[Tool Display Name]")
        self.setMinimumSize(400, 300)
        self.setup_ui()
```

#### **Standard UI Elements**
```python
def setup_ui(self):
    """Setup user interface"""
    layout = QtWidgets.QVBoxLayout(self)
    
    # Title
    title_label = QtWidgets.QLabel("[Tool Display Name]")
    title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
    
    # Main content
    content_group = QtWidgets.QGroupBox("Main Settings")
    content_layout = QtWidgets.QFormLayout(content_group)
    
    # Buttons
    button_layout = QtWidgets.QHBoxLayout()
    self.apply_btn = QtWidgets.QPushButton("Apply")
    self.cancel_btn = QtWidgets.QPushButton("Cancel")
    
    # Add to layout
    layout.addWidget(title_label)
    layout.addWidget(content_group)
    layout.addLayout(button_layout)
```

### 🔄 **Rule 10: Integration Flow**

#### **Standard Integration Process**
```python
def setup_[tool_name]_tools():
    """Setup all [tool name] tools"""
    add_[tool_name]_to_menu()
    add_[tool_name]_to_shelf()

# Auto-setup when imported
if __name__ == "__main__":
    setup_[tool_name]_tools()
```

#### **Auto-load Integration**
```python
# python/startup/auto_load.py
from mono_tools.[tool_name]_menu_integration import setup_[tool_name]_tools

def auto_load_mono_studio():
    # ... existing code
    setup_[tool_name]_tools()  # Add this line
```

## 🎯 **Consistency Checklist**

### **For Every New Tool:**

- [ ] **File naming** follows `[tool_name].py` pattern
- [ ] **Function naming** follows `show_[tool_name]()` pattern
- [ ] **Menu integration** follows standard pattern
- [ ] **Shelf integration** follows standard pattern
- [ ] **Package exports** added to `__init__.py`
- [ ] **Test files** created in `test_demo/`
- [ ] **Documentation** created in `docs/`
- [ ] **GUI standards** followed
- [ ] **Integration flow** implemented
- [ ] **Auto-load** updated

### **For Existing Tools:**

- [ ] **Rename files** to follow naming convention
- [ ] **Rename functions** to follow naming convention
- [ ] **Update imports** to use new names
- [ ] **Update menu/shelf** to use new names
- [ ] **Update documentation** to reflect changes
- [ ] **Test all functionality** after changes

## 🚀 **Migration Plan**

### **Phase 1: Standardize Naming**
1. Rename all files to follow convention
2. Rename all functions to follow convention
3. Update all imports
4. Test functionality

### **Phase 2: Standardize Structure**
1. Apply folder rules consistently
2. Standardize package exports
3. Standardize menu/shelf integration
4. Test all integrations

### **Phase 3: Standardize Documentation**
1. Create consistent documentation structure
2. Update all existing docs
3. Create missing documentation
4. Test documentation accuracy

## 📊 **Current Status**

### **Tools Following Rules:**
- ✅ Texture Search & Replace (mostly)
- ❌ File Manager (needs standardization)
- ❌ Material Loader (needs menu integration)

### **Tools Needing Updates:**
- File Manager: Add menu integration, standardize naming
- Material Loader: Add menu integration, standardize naming
- All tools: Standardize documentation

---

**Goal**: Tất cả tools phải tuân theo cùng một bộ quy tắc nhất quán để dễ maintain và mở rộng.
