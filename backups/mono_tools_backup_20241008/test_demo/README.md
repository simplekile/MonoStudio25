# Test & Demo Scripts

Thư mục chứa các script test và demo cho Mono Studio tools.

## 🧪 Test Scripts

### `test_pyside6.py`
Test PySide6 compatibility và các tính năng cơ bản.

```python
from mono_tools.test_demo import test_pyside6
test_pyside6()
```

### `verify_pyside6.py`
Verification đầy đủ cho PySide6 và tất cả components.

```python
from mono_tools.test_demo import verify_pyside6
verify_pyside6()
```

### `test_texture_search_replace.py`
Test cụ thể cho Texture Search & Replace tool.

```python
from mono_tools.test_demo import test_texture_search_replace
test_texture_search_replace()
```

## 🎬 Demo Scripts

### `demo_texture_search_replace.py`
Demo đầy đủ Texture Search & Replace tool với scene test.

```python
from mono_tools.test_demo import demo_texture_search_replace
demo_texture_search_replace()
```

### `quick_test_pyside6.py`
Test nhanh PySide6 và tạo dialog test.

```python
from mono_tools.test_demo import quick_test
quick_test()
```

### `test_menu_shelf.py`
Test menu và shelf integration.

```python
from mono_tools.test_demo import test_menu_shelf
test_menu_shelf()
```

## 🚀 Quick Start

### Test nhanh trong Houdini:
```python
# Test PySide6
exec(open("python/mono_tools/test_demo/quick_test_pyside6.py").read())

# Demo Texture Search & Replace
exec(open("python/mono_tools/test_demo/demo_texture_search_replace.py").read())
```

### Test từ package:
```python
# Import và chạy test
from mono_tools.test_demo import quick_test, demo_texture_search_replace

# Quick test
quick_test()

# Full demo
demo_texture_search_replace()
```

## 📋 Test Checklist

- [ ] PySide6 import successful
- [ ] Houdini environment detected
- [ ] Qt widgets creation works
- [ ] Texture Search & Replace tool loads
- [ ] Menu integration works
- [ ] Dialog displays correctly

## 🔧 Troubleshooting

### Import Error
```python
# Nếu gặp lỗi import, chạy từ thư mục gốc
import sys
sys.path.insert(0, "python")
from mono_tools.test_demo import quick_test
```

### Houdini Environment
```python
# Kiểm tra Houdini environment
try:
    import hou
    print("✅ Houdini environment OK")
except ImportError:
    print("❌ Not in Houdini environment")
```

## 📚 Usage Examples

### Test All Components
```python
from mono_tools.test_demo import verify_pyside6
verify_pyside6()
```

### Demo with Test Scene
```python
from mono_tools.test_demo import demo_texture_search_replace
demo_texture_search_replace()
```

### Quick PySide6 Test
```python
from mono_tools.test_demo import quick_test
quick_test()
```
