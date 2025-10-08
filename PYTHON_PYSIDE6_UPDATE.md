# PySide6 Update for Houdini 21

## ✅ Đã cập nhật thành công

Tất cả các file đã được cập nhật để sử dụng **PySide6** thay vì PySide2, tương thích với Houdini 21.

## 🔧 Files đã cập nhật

- `python/mono_tools/texture_search_replace.py` - Tool chính
- `python/mono_tools/texture_menu_integration.py` - Menu integration
- `python/mono_tools/__init__.py` - Package exports
- `python/mono_tools/qt.py` - Đã sử dụng PySide6 từ đầu
- `python/mono_tools/test_demo/` - Thư mục test và demo riêng
- `instructions.md` - Hướng dẫn AI luôn dùng PySide6

## 🧪 Test PySide6

### Quick Test
```python
# Chạy trong Houdini Python Console
exec(open("python/mono_tools/test_demo/quick_test_pyside6.py").read())
```

### Full Test
```python
# Chạy trong Houdini Python Console
from mono_tools import verify_pyside6
verify_pyside6()
```

### Demo Texture Tool
```python
# Chạy trong Houdini Python Console
from mono_tools import demo_texture_search_replace
demo_texture_search_replace()
```

### Test Texture Tool
```python
# Chạy trong Houdini Python Console
from mono_tools import show_texture_search_replace
show_texture_search_replace()
```

## 🚀 Sử dụng

1. **Từ menu**: `Mono Studio > Texture Search & Replace`
2. **Từ Python**: 
   ```python
   from mono_tools import show_texture_search_replace
   show_texture_search_replace()
   ```

## 📋 Tính năng

- ✅ PySide6 compatibility (Houdini 21+)
- ✅ Texture path search & replace
- ✅ Regex pattern support
- ✅ Auto backup before changes
- ✅ Preview before apply
- ✅ Menu integration
- ✅ Shelf integration

## 🔍 Troubleshooting

Nếu gặp lỗi import:
1. Đảm bảo đang chạy trong Houdini 21+
2. Kiểm tra Mono Studio đã được load
3. Chạy quick test để verify

## 📚 Documentation

Xem `docs/Texture_Search_Replace_Guide.md` để biết chi tiết cách sử dụng.
