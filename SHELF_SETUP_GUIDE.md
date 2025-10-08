# 🎬 Mono Studio - Professional Shelf Setup Guide

## 🎯 Cách chuyên nghiệp nhất: Shelf File (.shelf)

### **Tại sao chọn cách này?**
- ✅ **Official SideFX method**: Cách chính thức của SideFX
- ✅ **Production ready**: Được sử dụng trong pipeline thực tế
- ✅ **Version control friendly**: Dễ quản lý với Git
- ✅ **Cross-platform**: Hoạt động trên Windows/Mac/Linux
- ✅ **Persistent**: Không bị mất khi restart Houdini
- ✅ **Shareable**: Dễ chia sẻ với team

## 📋 Hướng dẫn Setup

### **Bước 1: Chạy Script tự động (Khuyến nghị)**
```bash
# Chạy script setup
python setup_shelf.py
```

### **Bước 2: Setup thủ công**
```bash
# 1. Tìm thư mục Houdini shelves
# Windows: %USERPROFILE%\Documents\houdini21.0\shelves\
# Mac: ~/Library/Preferences/houdini/21.0/shelves/
# Linux: ~/.houdini/21.0/shelves/

# 2. Copy file shelf
copy "shelves/MonoStudio.shelf" "%USERPROFILE%\Documents\houdini21.0\shelves\"

# 3. Restart Houdini
```

### **Bước 3: Verify Installation**
1. Mở Houdini
2. Tìm shelf tab "Mono Studio"
3. Test các tools

## 🛠️ Các Tools có sẵn

| Tool | Icon | Chức năng |
|------|------|-----------|
| **File Manager** | 📁 | Quản lý project và files |
| **MiniBar** | ⚡ | Truy cập nhanh files |
| **Material Loader** | 🎨 | Quản lý materials |
| **Texture Tools** | 🖼️ | Search & replace textures |
| **All Tools** | 🔧 | Mở tất cả tools |
| **Refresh Tools** | 🔄 | Reload modules |
| **Help** | ❓ | Hướng dẫn sử dụng |

## 🎯 Advanced Features

### **Shelf nâng cao (MonoStudioAdvanced.shelf)**
- **Separators**: Phân chia nhóm tools
- **Refresh Tools**: Reload modules khi cần
- **Help Tool**: Hiển thị hướng dẫn
- **Error handling**: Xử lý lỗi tốt hơn

### **Customization**
```python
# Thêm tool mới vào shelf
tool Custom_Tool
{
    label "My Custom Tool"
    icon "MISC_custom"
    script
    {
        import hou
        # Your custom code here
        print("Custom tool executed!")
    }
}
```

## 🔧 Troubleshooting

### **Lỗi thường gặp:**
1. **Shelf không xuất hiện**: Restart Houdini
2. **Tools không hoạt động**: Check Python path
3. **Import error**: Verify mono_tools installation

### **Debug commands:**
```python
# Check shelf installation
import hou
shelves = hou.shelves.shelves()
print("Available shelves:", list(shelves.keys()))

# Check Mono Studio shelf
mono_shelf = shelves.get("Mono Studio")
if mono_shelf:
    print("Mono Studio shelf found!")
    print("Tools:", [tool.name() for tool in mono_shelf.tools()])
else:
    print("Mono Studio shelf not found!")
```

## 🚀 Production Pipeline

### **Team Setup:**
1. **Developer**: Tạo và test shelf
2. **IT Admin**: Deploy shelf cho team
3. **Artist**: Sử dụng shelf trong production

### **Version Control:**
```bash
# Add shelf files to Git
git add shelves/*.shelf
git commit -m "Add Mono Studio shelf files"
git push
```

### **Deployment:**
```bash
# Deploy to team
./deploy_shelf.sh
# hoặc
python setup_shelf.py --deploy
```

## 📊 So sánh các phương pháp

| Method | Professional | Easy | Reliable | Team-friendly |
|--------|-------------|------|----------|---------------|
| **Shelf File** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Python Script** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Manual Setup** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐ |
| **Menu Integration** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |

## 🎉 Kết luận

**Shelf File (.shelf)** là cách chuyên nghiệp nhất vì:
- Được SideFX khuyến nghị
- Dễ quản lý và chia sẻ
- Hoạt động ổn định
- Phù hợp với production pipeline

**Khuyến nghị**: Sử dụng `setup_shelf.py` để tự động setup!
