# Texture Search & Replace Tool

Công cụ tìm kiếm và thay thế đường dẫn texture trong Houdini, được tích hợp vào Mono Studio.

**Tương thích**: Houdini 21+ (PySide6)

## Tính năng chính

- 🔍 **Tìm kiếm thông minh**: Tự động phát hiện các parameters chứa texture paths
- 🔄 **Thay thế linh hoạt**: Hỗ trợ text replacement và regex patterns
- 🎯 **Phạm vi tùy chọn**: Tìm kiếm trong network hiện tại, nodes được chọn, hoặc toàn bộ scene
- 💾 **Backup tự động**: Tự động tạo backup trước khi thay đổi
- 🎨 **Giao diện thân thiện**: GUI dễ sử dụng với preview kết quả

## Cách sử dụng

### 1. Mở công cụ

Có **4 cách** để mở Texture Search & Replace:

#### 🎯 **Cách 1: Từ Menu (Khuyến nghị)**
- `Menu Bar > Mono Studio > Texture Search & Replace`

#### 🎯 **Cách 2: Từ Shelf**
- `Shelf > Mono Studio > Texture Search & Replace`

#### 🎯 **Cách 3: Từ Python Console**
```python
from mono_tools import show_texture_search_replace
show_texture_search_replace()
```

#### 🎯 **Cách 4: Từ Script File**
```python
exec(open("python/mono_tools/test_demo/demo_texture_search_replace.py").read())
```

### 2. Cấu hình tìm kiếm

#### Pattern cần tìm
- **Text đơn giản**: `D:/OldProject/Textures/`
- **Regex pattern**: `(\d{4})\.(exr|jpg|png)` (để tìm UDIM numbers)

#### Thay thế bằng
- **Text đơn giản**: `E:/NewProject/Assets/`
- **Regex replacement**: `<UDIM>.\2` (sử dụng captured groups)

#### Tùy chọn
- ☑️ **Phân biệt hoa thường**: Bật/tắt case sensitivity
- ☑️ **Sử dụng Regular Expression**: Bật/tắt regex mode
- ☑️ **Tạo backup**: Tự động backup file trước khi thay đổi

#### Phạm vi tìm kiếm
- 🔸 **Network hiện tại**: Chỉ tìm trong network đang mở
- 🔸 **Nodes được chọn**: Chỉ tìm trong các nodes đã chọn
- 🔸 **Toàn bộ scene**: Tìm trong toàn bộ scene

### 3. Thực hiện thay đổi

1. **Preview**: Click "Preview" để xem trước các thay đổi
2. **Kiểm tra kết quả**: Xem danh sách các thay đổi sẽ được thực hiện
3. **Apply**: Click "Apply Changes" để áp dụng thay đổi

## Ví dụ sử dụng

### Ví dụ 1: Thay đổi đường dẫn project

**Tình huống**: Chuyển project từ `D:/OldProject/` sang `E:/NewProject/`

**Cấu hình**:
- Pattern cần tìm: `D:/OldProject/`
- Thay thế bằng: `E:/NewProject/`
- Phạm vi: Toàn bộ scene
- Backup: Bật

**Kết quả**: Tất cả texture paths sẽ được cập nhật từ đường dẫn cũ sang đường dẫn mới.

### Ví dụ 2: Chuyển đổi UDIM format

**Tình huống**: Chuyển từ UDIM numbers sang `<UDIM>` tags

**Cấu hình**:
- Pattern cần tìm: `(\d{4})\.(exr|jpg|png)` (regex)
- Thay thế bằng: `<UDIM>.\2` (regex)
- Phạm vi: Toàn bộ scene

**Kết quả**: 
- `texture_1001.exr` → `texture_<UDIM>.exr`
- `material_1002.jpg` → `material_<UDIM>.jpg`

### Ví dụ 3: Thay đổi tên thư mục

**Tình huống**: Đổi tên thư mục texture

**Cấu hình**:
- Pattern cần tìm: `Textures/`
- Thay thế bằng: `Assets/Textures/`
- Phạm vi: Network hiện tại

## Các loại parameters được hỗ trợ

Tool tự động phát hiện các parameters chứa texture paths dựa trên:

### Tên parameter
- `tex*`, `texture*`, `map*`, `file*`, `filename*`
- `diffuse*`, `normal*`, `bump*`, `displacement*`
- `roughness*`, `metallic*`, `emission*`, `opacity*`

### Nội dung value
- Chứa đường dẫn file (`/` hoặc `\`)
- Có extension ảnh (`.exr`, `.jpg`, `.jpeg`, `.png`, `.tif`, `.tiff`, `.hdr`, `.tga`)

## Backup và an toàn

### Tự động backup
- File được backup trước khi thay đổi
- Backup được lưu trong thư mục `backups/` cùng cấp với file .hip
- Tên backup: `filename_backup_YYYYMMDD_HHMMSS.hip`

### Khôi phục
Nếu cần khôi phục:
1. Mở file backup từ thư mục `backups/`
2. Save as với tên file gốc

## Troubleshooting

### Lỗi thường gặp

**"Không tìm thấy pattern nào phù hợp"**
- Kiểm tra pattern có đúng không
- Thử với phạm vi tìm kiếm rộng hơn
- Kiểm tra case sensitivity

**"Lỗi Regular Expression"**
- Kiểm tra syntax regex
- Escape các ký tự đặc biệt
- Test regex trước khi sử dụng

**"Không thể tạo backup"**
- Kiểm tra quyền ghi file
- Đảm bảo file đã được save
- Kiểm tra dung lượng ổ đĩa

### Tips sử dụng

1. **Luôn preview trước khi apply** để kiểm tra kết quả
2. **Sử dụng backup** để an toàn
3. **Test với phạm vi nhỏ** trước khi áp dụng toàn bộ scene
4. **Regex patterns** mạnh mẽ hơn text replacement
5. **Case insensitive** hữu ích khi không chắc chắn về hoa thường

## API Reference

### Hàm chính

```python
from mono_tools.texture_search_replace import show_texture_search_replace

# Mở dialog
dialog = show_texture_search_replace()
```

### Tích hợp menu

```python
from mono_tools.texture_menu_integration import setup_texture_tools

# Thiết lập menu và shelf
setup_texture_tools()
```

## Changelog

### v1.0.0
- ✅ Tìm kiếm và thay thế texture paths
- ✅ Hỗ trợ regex patterns
- ✅ Giao diện GUI thân thiện
- ✅ Backup tự động
- ✅ Tích hợp menu Houdini
- ✅ Preview trước khi apply
