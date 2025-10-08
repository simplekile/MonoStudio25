# Mono Studio - Tool Folder Strategy

## 🎯 **Khi nào nên tạo folder riêng cho Tool?**

### ✅ **NÊN tạo folder riêng khi:**

#### **1. Tool có nhiều file liên quan (4+ files)**
```
python/mono_tools/
└── file_manager/                    # ✅ NÊN tạo folder
    ├── __init__.py
    ├── file_manager.py              # Main tool
    ├── file_manager_api.py          # API wrapper
    ├── fm_helpers.py                # Helper functions
    ├── fm_models.py                 # Data models
    ├── fm_minibar.py                # MiniBar component
    └── fm_manager.py                # Manager class
```

#### **2. Tool có sub-components phức tạp**
```
python/mono_tools/
└── material_system/                 # ✅ NÊN tạo folder
    ├── __init__.py
    ├── material_loader.py           # Main loader
    ├── texture_search_replace.py    # Texture tool
    ├── material_browser.py          # Browser component
    ├── material_preview.py          # Preview component
    └── material_export.py           # Export functionality
```

#### **3. Tool có nhiều loại file khác nhau**
```
python/mono_tools/
└── render_pipeline/                 # ✅ NÊN tạo folder
    ├── __init__.py
    ├── render_manager.py            # Main manager
    ├── render_settings.py           # Settings
    ├── render_queue.py              # Queue management
    ├── render_export.py             # Export functions
    ├── render_templates/            # Sub-folder for templates
    │   ├── __init__.py
    │   ├── houdini_templates.py
    │   └── maya_templates.py
    └── render_utils.py              # Utilities
```

### ❌ **KHÔNG nên tạo folder khi:**

#### **1. Tool đơn giản (1-3 files)**
```
python/mono_tools/
├── texture_search_replace.py        # ❌ KHÔNG cần folder
├── texture_menu_integration.py      # Chỉ 2 files
└── material_loader.py               # ❌ KHÔNG cần folder
```

#### **2. Tool chỉ có 1 file chính**
```
python/mono_tools/
├── simple_tool.py                   # ❌ KHÔNG cần folder
├── qt.py                           # ❌ KHÔNG cần folder
└── utils.py                        # ❌ KHÔNG cần folder
```

#### **3. Tool nhỏ, ít chức năng**
```
python/mono_tools/
├── color_picker.py                  # ❌ KHÔNG cần folder
├── unit_converter.py                # ❌ KHÔNG cần folder
└── system_info.py                   # ❌ KHÔNG cần folder
```

## 📊 **Phân tích cấu trúc hiện tại**

### **File Manager** - ✅ **NÊN tạo folder**
```
Hiện tại: 6 files scattered
├── file_manager.py
├── file_manager_api.py
├── fm_helpers.py
├── fm_manager.py
├── fm_minibar.py
└── fm_models.py

Nên chuyển thành:
python/mono_tools/
└── file_manager/
    ├── __init__.py
    ├── file_manager.py
    ├── file_manager_api.py
    ├── fm_helpers.py
    ├── fm_manager.py
    ├── fm_minibar.py
    └── fm_models.py
```

### **Texture Search & Replace** - ❌ **KHÔNG cần folder**
```
Hiện tại: 2 files
├── texture_search_replace.py
└── texture_menu_integration.py

Giữ nguyên vì chỉ có 2 files
```

### **Material Loader** - ❌ **KHÔNG cần folder**
```
Hiện tại: 1 file
└── material_loader.py

Giữ nguyên vì chỉ có 1 file
```

## 🔄 **Migration Strategy**

### **Bước 1: Xác định tool cần folder**
```python
# Tool có 4+ files → Tạo folder
file_manager_files = [
    'file_manager.py',
    'file_manager_api.py', 
    'fm_helpers.py',
    'fm_manager.py',
    'fm_minibar.py',
    'fm_models.py'
]
# → Tạo folder: file_manager/
```

### **Bước 2: Tạo folder structure**
```
python/mono_tools/
└── file_manager/
    ├── __init__.py                  # Package exports
    ├── file_manager.py              # Main tool
    ├── file_manager_api.py          # API wrapper
    ├── fm_helpers.py                # Helper functions
    ├── fm_manager.py                # Manager class
    ├── fm_minibar.py                # MiniBar component
    └── fm_models.py                 # Data models
```

### **Bước 3: Cập nhật imports**
```python
# python/mono_tools/file_manager/__init__.py
from .file_manager import show_mono_file_manager
from .file_manager_api import FileManagerWrapper
from .fm_minibar import show_mono_minibar

__all__ = [
    'show_mono_file_manager',
    'FileManagerWrapper', 
    'show_mono_minibar'
]

# python/mono_tools/__init__.py
from .file_manager import show_mono_file_manager
# Thay vì: from .file_manager import show_mono_file_manager
```

## 📋 **Folder Naming Conventions**

### **Tool Folder Names**
- `snake_case` - All folder names
- `[feature_name]/` - Feature-based naming
- `[tool_name]/` - Tool-based naming

### **Examples**
```
✅ GOOD:
├── file_manager/
├── material_system/
├── render_pipeline/
└── animation_tools/

❌ BAD:
├── FileManager/
├── material-system/
├── render_pipeline_tools/
└── anim/
```

## 🎯 **Decision Matrix**

| Tool Files | Complexity | Sub-components | Folder Needed? |
|------------|------------|----------------|----------------|
| 1-2 files  | Simple     | None          | ❌ NO          |
| 3 files    | Medium     | None          | ❌ NO          |
| 4+ files   | Medium     | None          | ✅ YES         |
| 3+ files   | High       | Multiple      | ✅ YES         |
| 2+ files   | High       | Multiple      | ✅ YES         |

## 🚀 **Implementation Plan**

### **Phase 1: Analyze Current Tools**
1. Count files per tool
2. Identify complex tools
3. Plan folder structure

### **Phase 2: Migrate Complex Tools**
1. Create folders for 4+ file tools
2. Move files to folders
3. Update imports
4. Test functionality

### **Phase 3: Update Documentation**
1. Update folder guidelines
2. Update import examples
3. Update development docs

## 📚 **Best Practices**

### **1. Keep It Simple**
- Don't over-organize
- Only create folders when necessary
- Maintain flat structure when possible

### **2. Consistent Naming**
- Use snake_case for all folders
- Use descriptive names
- Follow existing patterns

### **3. Clear Boundaries**
- Each folder = one major feature
- Clear separation of concerns
- Easy to navigate

### **4. Future-Proof**
- Plan for growth
- Flexible structure
- Easy to extend

## 🔍 **Current Status Analysis**

### **Tools that NEED folders:**
- **File Manager** (6 files) → `file_manager/`

### **Tools that DON'T need folders:**
- **Texture Search & Replace** (2 files)
- **Material Loader** (1 file)
- **Qt Utilities** (1 file)
- **General Utils** (1 file)

### **Test/Demo files:**
- **All tests** → `test_demo/` (already organized)

---

**Recommendation**: Chỉ tạo folder cho File Manager vì có 6 files. Các tool khác giữ nguyên cấu trúc flat.
