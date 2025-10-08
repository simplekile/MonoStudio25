# Mono Studio v2.0 - Houdini Production Tools

## 🎬 Overview
Professional Houdini tools suite for VFX production workflows. Features intelligent file management, shot organization, and seamless Houdini integration.

## ✨ Key Features

### 🗂️ **File Manager + Movable MiniBar**
- **Smart File Scanning**: Auto-scan `02_shots/03_lighting` for `.hip/.hiplc/.hipnc` files
- **Shot Detection**: Intelligent shot naming from file patterns (`Sh001`, `SH010`, etc.)
- **Version Management**: Automatic version parsing and latest version selection
- **Movable MiniBar**: Frameless, draggable widget with position memory
- **One-Click Open**: Click shot name → opens file directly in Houdini
- **Full Manager**: Complete table view with sorting, filtering, and details

### 🎯 **Smart UI Features**
- **Dark Theme**: Professional UI matching Houdini's aesthetic  
- **Context Menu**: Right-click for Lock/Unlock, Reset position, Close
- **Auto-Positioning**: Remembers position relative to Houdini window
- **Explorer Integration**: Double-click to open folders in Windows Explorer
- **Path Copying**: Copy file paths to clipboard

## 📦 Package Structure
```
MonoStudio/
├── package.json                    # Houdini package definition
├── python/
│   ├── mono_tools/
│   │   ├── __init__.py            # Main package initialization
│   │   ├── file_manager.py        # Complete file manager system
│   │   ├── material_loader.py     # Material batch operations
│   │   └── utils.py               # Utility functions
│   └── startup/
│       ├── auto_load.py           # Auto-startup logic
│       └── 123.py                 # Package startup hook
├── scripts/                       # Additional scripts
├── otls/                         # Houdini digital assets
├── toolbar/                      # Shelf tools & UI elements
├── config/                       # Configuration files
└── docs/                         # Documentation
```

## 🚀 Installation

## ✅ Requirements

- Houdini 21+
- Windows 10/11
- Python 3.11 (the one bundled with Houdini)
- PySide6 (bundled with Houdini)

### **Method 1: Package System (Recommended)**

1. **Create package file:**
   ```
   C:/Users/[USERNAME]/Documents/houdini21.0/packages/MONO_STUDIO.json
   ```

2. **Package content (đồng bộ với file `MonoStudio_package.json` trong repo):**
   ```json
   {
   "env":[
  {"MONO_STUDIO" : "d:/Dropbox/Stock/Plugin/HOU/MonoStudio25"},
   {"MONO_VERSION" : "2.0.0"},
  {"HOUDINI_PATH" : "$MONO_STUDIO;&"},
  {"PYTHONPATH" : "$MONO_STUDIO/python;&"},
   {"HOUDINI_OTLSCAN_PATH" : "$MONO_STUDIO/otls;&"},
   {"HOUDINI_TOOLBAR_PATH" : "$MONO_STUDIO/toolbar;&"}
   ]
   }
   ```

3. (Tuỳ chọn) Nếu muốn tự động nạp các script UI-ready/startup từ thư mục dự án, bạn có thể thêm `;$MONO_STUDIO/python/startup` vào `PYTHONPATH` trong package.

### **Method 2: Alternative Startup Locations (Per SideFX Documentation)**

According to [SideFX official docs](https://www.sidefx.com/docs/houdini/hom/locations.html), you can place startup scripts in multiple locations:

1. **UI-Ready Startup (Recommended for UI tools):**
   ```
   $HOUDINI_USER_PREF_DIR/python3.11libs/uiready.py
   ```
  - Runs after UI is fully loaded (perfect for MiniBar)
   - Only runs in interactive Houdini sessions

2. **Session Startup:**
   ```
   $HOUDINI_USER_PREF_DIR/scripts/123.py
   ```
   - Runs when Houdini starts without scene file
   - Traditional method, works reliably

3. **Package-Managed Startup:**
   Since our package sets `HOUDINI_PATH`, you can also use:
   ```
  $MONO_STUDIO/python3.11libs/uiready.py
   $MONO_STUDIO/scripts/123.py
   ```

**Choose any method that suits your workflow - all are officially supported!**

## ⚡ Quick Start (Tiếng Việt)

1. Tạo file `C:/Users/[USERNAME]/Documents/houdini21.0/packages/MONO_STUDIO.json`.
2. Dán nội dung package mẫu ở trên và chỉnh `MONO_STUDIO` → `D:/Dropbox/Stock/Plugin/HOU/MonoStudio25`.
3. Mở Houdini 21+. MiniBar sẽ tự hiện sau khi UI sẵn sàng.
4. Nếu không thấy, xem mục Troubleshooting bên dưới.

## 🎯 Usage

### **Auto-Startup**
MiniBar automatically appears when Houdini starts with these messages:
```
🎬 Mono Studio 123.py startup loading...
📁 Added python path: d:/Dropbox/Stock/Plugin/HOU/MonoStudio25\python
🔧 Set MONO_STUDIO: d:/Dropbox/Stock/Plugin/HOU/MonoStudio25
📦 Modules imported successfully
⏱️ MiniBar creation deferred until UI ready
🎯 Creating MiniBar...
✅ MiniBar instance created
📍 MiniBar positioned at (1340, 74)
✅ Mono Studio MiniBar loaded!
💡 Click shot name → open file | Click ⚡ → full manager
```

### **Manual Usage**
```python
# Import package
import mono_tools

# Open full File Manager
mono_tools.open_file_manager()

# Open MiniBar
mono_tools.open_minibar()

# Direct access
from mono_tools import show_mono_file_manager, show_mono_minibar
show_mono_minibar()
```

### **File Manager Workflow**
1. **Set Project Root**: Browse to your project directory
2. **Auto-Scan**: Files in `02_shots/03_lighting` are automatically found
3. **Shot Selection**: Click shot name in MiniBar dropdown to open latest version
4. **Full Manager**: Click ⚡ button for complete file table with details

## 🔧 Configuration

### **Project Structure Expected**
```
ProjectRoot/
└── 02_shots/
    └── 03_lighting/
        ├── Sh001/
        │   ├── Sh001_lighting_v001.hip
        │   ├── Sh001_lighting_v002.hip
        │   └── Sh001_lighting_v003.hip
        └── Sh010/
            ├── Sh010_lighting_v001.hipnc
            └── Sh010_lighting_v002.hipnc
```

### **File Naming Convention**
### **Config keys (`config/settings.json`)**

- `mono_studio.version`: phiên bản gói.
- `mono_studio.auto_load`: tự động nạp module khi khởi động.
- `mono_studio.show_minibar_on_start`: hiển thị MiniBar khi Houdini mở.
- `mono_studio.minibar_position.x|y`: toạ độ lưu của MiniBar.
- `mono_studio.file_manager.scan_on_expand`: chỉ scan khi mở rộng bảng.
- `mono_studio.file_manager.default_extensions`: phần mở rộng file Houdini.
- `mono_studio.file_manager.max_recent_files`: số file gần đây tối đa hiển thị.
- `mono_studio.ui_theme.style`: `dark` hoặc `light`.
- `mono_studio.ui_theme.accent_color`: màu nhấn dạng hex.
- **Shot Pattern**: `Sh001`, `SH010`, etc.
- **Version Pattern**: `v001`, `v002`, `v123`
- **Supported Extensions**: `.hip`, `.hiplc`, `.hipnc`

## 🛠️ Development

## 🧩 Troubleshooting

- MiniBar không hiện khi mở Houdini:
  - Kiểm tra biến môi trường trong Python Shell của Houdini:
    ```python
    import os
    print(os.environ.get('MONO_STUDIO'))
    ```
    Kỳ vọng: `D:/Dropbox/Stock/Plugin/HOU/MonoStudio25`
  - Thử import thủ công:
    ```python
    import mono_tools
    from mono_tools import open_minibar
    open_minibar()
    ```
  - Xem console có log khởi động như phần Auto-Startup.

- Import lỗi `ModuleNotFoundError: No module named 'mono_tools'`:
  - Kiểm tra `PYTHONPATH` trong package có chứa `$MONO_STUDIO/python`.
  - Đường dẫn `MONO_STUDIO` đã đúng thư mục `MonoStudio25` chưa.

- UI bị treo khi khởi động:
  - Dùng UI-Ready startup (`python3.11libs/uiready.py`) thay vì `scripts/123.py`.
  - Đảm bảo chỉ một cơ chế startup hoạt động để tránh nạp trùng.

- Không scan thấy file `.hip`:
  - Xác nhận cấu trúc thư mục đúng như phần Project Structure.
  - Cập nhật `default_extensions` trong `config/settings.json` nếu cần.

### **Adding New Tools**
1. Create new module in `python/mono_tools/`
2. Update `__init__.py` to export new functions
3. Add to `__all__` list for public API

### **Extending File Manager**
- Modify `SUBPATH` for different folder structure
- Update `HOUDINI_EXTS` for additional file types
- Customize `_infer_shot()` for different naming conventions

### **Debugging**
Enable verbose logging:
```python
import mono_tools
# Check environment
import os
print("MONO_STUDIO:", os.environ.get('MONO_STUDIO'))

# Manual import test
from mono_tools.file_manager import show_mono_minibar
minibar = show_mono_minibar()
```

## 🎨 Technical Details

### **Architecture**
- **PySide6**: Modern Qt interface for Houdini 21+
- **QSettings**: Persistent user preferences and position memory
- **QTimer.singleShot()**: Deferred UI creation for stability
- **Package System**: Clean Houdini integration via JSON configuration

### **Key Classes**
- `MonoFileManager`: Full dialog with table view and controls
- `MonoFileMiniBar`: Compact draggable widget with dropdown
- `FileManagerWrapper`: Compatibility wrapper for legacy systems
- `_Model`: QStandardItemModel for file data management

## 🧾 Version History

### **v2.0.0** (Current)
- ✅ Complete rewrite with modern PySide2 UI
- ✅ Movable MiniBar with position memory  
- ✅ Smart shot detection and version management
- ✅ One-click file opening in Houdini
- ✅ Package system integration
- ✅ Auto-startup with proper UI deferral
- ✅ Dark theme matching Houdini aesthetic

### **v1.x** (Legacy)
- Basic file management
- Simple UI without positioning
- Manual startup required

## 📞 Support

For issues or feature requests:
1. Check console output for error messages
2. Verify project structure matches expected format
3. Ensure Houdini 20.5+ and PySide2 availability
4. Test manual import: `import mono_tools`

## 📄 License

Professional Houdini production tools suite by DTA Studio.