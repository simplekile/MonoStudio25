# Mono Studio - Folder Recommendation

## 🎯 **Kết quả phân tích cấu trúc hiện tại**

### 📊 **Tool Analysis Results:**

| Tool Name | Files Count | Files | Recommendation |
|-----------|-------------|-------|----------------|
| **file_manager** | 5 files | file_manager.py, fm_helpers.py, fm_manager.py, fm_minibar.py, fm_models.py | ✅ **CREATE FOLDER** |
| file_manager_api | 1 file | file_manager_api.py | ❌ No folder needed |
| material_loader | 1 file | material_loader.py | ❌ No folder needed |
| texture_search_replace | 2 files | texture_search_replace.py, texture_menu_integration.py | ❌ No folder needed |
| qt.py | 1 file | qt.py | ❌ No folder needed |
| utils.py | 1 file | utils.py | ❌ No folder needed |

## 🎯 **Khuyến nghị cụ thể**

### ✅ **NÊN tạo folder cho:**

#### **File Manager** (5 files)
```
python/mono_tools/
└── file_manager/                    # ✅ TẠO FOLDER
    ├── __init__.py                  # Package exports
    ├── file_manager.py              # Main tool
    ├── fm_helpers.py                # Helper functions
    ├── fm_manager.py                # Manager class
    ├── fm_minibar.py                # MiniBar component
    └── fm_models.py                 # Data models
```

**Lý do:**
- Có 5 files liên quan đến file management
- Có sub-components phức tạp (API, helpers, models, minibar)
- Dễ quản lý và maintain
- Tuân theo quy tắc "4+ files cần folder"

### ❌ **KHÔNG nên tạo folder cho:**

#### **Texture Search & Replace** (2 files)
```
python/mono_tools/
├── texture_search_replace.py        # ❌ KHÔNG cần folder
└── texture_menu_integration.py      # Chỉ 2 files
```

#### **Material Loader** (1 file)
```
python/mono_tools/
└── material_loader.py               # ❌ KHÔNG cần folder
```

#### **Utility Files** (1 file each)
```
python/mono_tools/
├── qt.py                           # ❌ KHÔNG cần folder
└── utils.py                        # ❌ KHÔNG cần folder
```

## 🚀 **Migration Plan**

### **Bước 1: Tạo folder structure**
```bash
mkdir python/mono_tools/file_manager
```

### **Bước 2: Tạo __init__.py**
```python
# python/mono_tools/file_manager/__init__.py
from .file_manager import show_mono_file_manager
from .file_manager_api import FileManagerWrapper
from .fm_minibar import show_mono_minibar
from .fm_manager import MonoFileManager
from .fm_models import FileModel
from .fm_helpers import parse_ver, increment_version_and_backup

__all__ = [
    'show_mono_file_manager',
    'FileManagerWrapper',
    'show_mono_minibar', 
    'MonoFileManager',
    'FileModel',
    'parse_ver',
    'increment_version_and_backup'
]
```

### **Bước 3: Di chuyển files**
```bash
move python/mono_tools/file_manager.py python/mono_tools/file_manager/
move python/mono_tools/fm_helpers.py python/mono_tools/file_manager/
move python/mono_tools/fm_manager.py python/mono_tools/file_manager/
move python/mono_tools/fm_minibar.py python/mono_tools/file_manager/
move python/mono_tools/fm_models.py python/mono_tools/file_manager/
```

### **Bước 4: Cập nhật imports**
```python
# python/mono_tools/__init__.py
from .file_manager import show_mono_file_manager, FileManagerWrapper, show_mono_minibar
# Thay vì import trực tiếp từ các file riêng lẻ
```

### **Bước 5: Test functionality**
- Test menu integration
- Test shelf integration  
- Test Python imports
- Test MiniBar functionality

## 📋 **Cấu trúc sau migration**

```
python/mono_tools/
├── __init__.py                      # Main package exports
├── qt.py                           # Qt utilities (standalone)
├── utils.py                        # General utilities (standalone)
├── material_loader.py              # Material tool (standalone)
├── texture_search_replace.py       # Texture tool (standalone)
├── texture_menu_integration.py     # Texture integration (standalone)
├── file_manager/                   # File manager package
│   ├── __init__.py
│   ├── file_manager.py
│   ├── fm_helpers.py
│   ├── fm_manager.py
│   ├── fm_minibar.py
│   └── fm_models.py
└── test_demo/                      # Test & demo files
    ├── test_*.py
    └── demo_*.py
```

## 🎯 **Lợi ích của việc tạo folder**

### **Cho File Manager:**
1. **Tổ chức tốt hơn** - 5 files liên quan được nhóm lại
2. **Dễ maintain** - Tìm file nhanh hơn
3. **Scalable** - Dễ thêm features mới
4. **Clear boundaries** - Rõ ràng về chức năng
5. **Import management** - Centralized exports

### **Cho các tool khác:**
1. **Giữ nguyên cấu trúc flat** - Đơn giản, dễ hiểu
2. **Không over-organize** - Tránh tạo quá nhiều folder
3. **Consistent** - Cùng pattern cho tools đơn giản

## ⚠️ **Lưu ý quan trọng**

### **Chỉ migrate File Manager:**
- Các tool khác giữ nguyên cấu trúc hiện tại
- Không tạo folder cho tools đơn giản
- Tuân theo nguyên tắc "4+ files mới cần folder"

### **Test kỹ lưỡng:**
- Đảm bảo tất cả imports hoạt động
- Test menu/shelf integration
- Test MiniBar functionality
- Test file manager features

## 📚 **Tài liệu tham khảo**

- `docs/Tool_Folder_Strategy.md` - Chi tiết về khi nào tạo folder
- `instructions.md` - Hướng dẫn development
- `python/simple_analyze.py` - Script phân tích cấu trúc

---

**Kết luận**: Chỉ tạo folder cho **File Manager** vì có 5 files. Các tool khác giữ nguyên cấu trúc flat.
