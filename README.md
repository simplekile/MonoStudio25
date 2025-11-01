# Mono Studio v2.4.0

A professional Houdini package with powerful tools for file management, material loading, and texture search & replace.

## 🚀 **Quick Start**

### **Setup:**

#### **1. Install Package:**
Copy `MonoStudio_package.json` to your Houdini packages directory:
   - **Windows**: `Documents/houdini21.0/packages/`
   - **macOS**: `~/Library/Preferences/houdini/21.0/packages/`
   - **Linux**: `~/houdini21.0/packages/`

#### **2. Install Shelf (Optional but Recommended):**
Copy shelf files to your Houdini shelves directory:
   - **Windows**: `Documents/houdini21.0/shelves/`
   - **macOS**: `~/Library/Preferences/houdini/21.0/shelves/`
   - **Linux**: `~/.houdini/21.0/shelves/`

   Available shelf files:
   - `MonoStudio.shelf` - Basic tools
   - `MonoStudio_Professional.shelf` - Professional workflow tools
   - `MonoStudioAdvanced.shelf` - Advanced features

#### **3. Restart Houdini**

#### **4. Verify Installation:**
- ✅ Check for "Mono Studio" menu in menu bar
- ✅ Check for "Mono Studio" shelf tab
- ✅ Check for MiniBar in top-right corner

## 🛠️ **Tools Included**

### **1. File Manager**
- **Access**: Menu + Shelf + Python + MiniBar
- **Features**: 
  - File browsing, version management, project organization
  - New Folder: Auto-create complete asset/shot structure
  - New File: Auto-naming with smart prefixes
  - Asset Types UI management
  - Subdepartment support
- **MiniBar**: Quick access in top-right corner with draggable positioning

### **2. Material Loader**
- **Access**: Menu + Shelf + Python
- **Features**: Redshift and Karma material creation from texture folders
- **Support**: UDIM, texture parsing, automatic material setup

### **3. Texture Search & Replace**
- **Access**: Menu + Shelf + Python
- **Features**: Search and replace texture paths in Houdini scene
- **Support**: Regex patterns, backup functionality, batch processing

## 📁 **Project Structure**

```
MonoStudio25/
├── README.md                    # This file
├── MonoStudio_package.json      # Houdini package definition
├── instructions.md              # Development guidelines
├── LICENSE                      # License file
├── python/                      # Python package
│   └── mono_tools/              # Main tools package
│       ├── file_manager/        # File Manager tool
│       ├── material_loader/     # Material Loader tool
│       ├── texture_search_replace/  # Texture Search & Replace
│       └── assets_manager/      # Assets Manager (in development)
├── menus/                       # Houdini menu definitions
├── shelves/                     # Houdini shelf definitions
├── scripts/                     # Startup scripts
├── python3.11libs/              # Houdini startup scripts
├── otls/                        # Houdini OTL files
├── toolbar/                     # Houdini toolbar files
├── config/                      # Configuration files
│   ├── asset_departments.json   # Asset department config
│   └── shot_departments.json    # Shot department config
└── docs/                        # Documentation
```

## 🔧 **Development**

### **Requirements:**
- Houdini 21+ (Python 3.11)
- PySide6 (included in Houdini 21+)

### **Development Workflow:**
1. Edit code in `python/mono_tools/`
2. Changes reflect immediately (no reinstall needed)
3. Test in Houdini
4. Use `install.py` for distribution

### **Code Organization:**
- **Tools**: Each tool has its own folder
- **Utilities**: Helper functions in `utilities/`
- **Testing**: Test scripts in `testing/`
- **Analysis**: Analysis tools in `analysis/`
- **Migration**: Migration tools in `migration/`

## 📋 **Setup Details**

### **What gets copied:**
- Only `MonoStudio_package.json` is copied to Houdini packages directory
- Package points to current directory (no copying of folders)
- All tools work from original location

### **Benefits:**
- ✅ **No copying** - Works from current folder
- ✅ **Auto-updates** - Changes reflect immediately
- ✅ **Space efficient** - No duplicate files
- ✅ **Easy development** - Edit and test in place

## 🎯 **Usage Examples**

### **Python Console:**
```python
# Import tools
from mono_tools import show_mono_file_manager, show_material_loader, show_texture_search_replace

# Show tools
show_mono_file_manager()
show_material_loader()
show_texture_search_replace()
```

### **Menu Access:**
- **Mono Studio** → **File Manager**
- **Mono Studio** → **Material Loader**
- **Mono Studio** → **Texture Search & Replace**

### **Shelf Access:**
- **Mono Studio** shelf with tools:
  - 📁 **File Manager** - Open main file manager dialog
  - ⚡ **MiniBar** - Quick access file browser (top-right corner)
  - 🎨 **Material Loader** - Load materials from texture folders
  - 🖼️ **Texture Tools** - Search & replace texture paths
- Click buttons to launch tools
- Available shelf variants:
  - `MonoStudio.shelf` - Basic tools
  - `MonoStudio_Professional.shelf` - Professional workflow
  - `MonoStudioAdvanced.shelf` - Advanced features

## 🆘 **Troubleshooting**

### **Tools not showing:**
- Check console for error messages
- Verify package.json is in Houdini packages directory
- Restart Houdini completely

### **Import errors:**
- Ensure Houdini 21+ is being used
- Check Python path in package.json
- Verify all dependencies are available

## 📚 **Documentation**

- **instructions.md** - Development guidelines
- **docs/** - Additional documentation

## 📄 **License**

See LICENSE file for details.

## 🎉 **Version History**

### **v2.4.0** (Current) - UI Improvements & Styling
- **Centralized styling system** - Extracted all styles to `ui/styles.py` module
- **Enhanced file display** - Shows full file name instead of just shot name
- **Smart note display** - Notes shown smaller, dimmed, and properly separated from file name
- **Improved hover behavior** - Unified hover for menu items with notes
- **Auto-refresh on dropdowns** - Automatically refreshes files when opening any menu (type, dept, user, files)
- **Cleaner current file indicator** - Removed emoji and "(Current)" text, uses bold only
- **Consistent UI styling** - All dialogs now use centralized style system
- **Fixed user filter** - Properly filters by user when subfolder is "all files"
- **Better file parsing** - Improved handling of complex note patterns in file names

### **v2.3.0** - Major Improvements
- Custom styled dialogs (ChoiceDialog, InputDialog) replacing Houdini native
- Asset vs Shot department separation with dedicated configs
- UI modularization with reusable components (MonoBaseDialog, SmartLineEdit)
- SmartLineEdit with Chrome-style autocomplete
- Asset Types UI management (Add/Edit/Remove)
- Subdepartment support matching template structure
- New Folder/File features with auto-naming
- MiniBar position fixes and improvements
- Project cleanup and folder organization
- Simplified startup system
- Better error handling and debug mode

### **v2.2.0**
- Simplified startup system (200+ → 45 lines)
- Menu integration fixes
- Performance optimizations
- Position system simplification
- New File/Folder creation features

### **v2.1.x**
- Various bug fixes and improvements

### **v2.0.0**
- PySide6 support
- Clean project structure
- Professional installer

### **v1.x**
- Legacy versions

---

**🎊 Mono Studio - Professional Houdini Tools Package!**
