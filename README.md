# Mono Studio v2.0.0

A professional Houdini package with powerful tools for file management, material loading, and texture search & replace.

## 🚀 **Quick Start**

### **Setup:**
1. Copy `MonoStudio_package.json` to your Houdini packages directory:
   - **Windows**: `Documents/houdini21.0/packages/`
   - **macOS**: `~/Library/Preferences/houdini/21.0/packages/`
   - **Linux**: `~/houdini21.0/packages/`

2. Restart Houdini

3. Check for "Mono Studio" menu and shelf
4. Check for MiniBar in top-right corner

## 🛠️ **Tools Included**

### **1. File Manager**
- **Access**: Menu + Shelf + Python
- **Features**: File browsing, version management, project organization
- **MiniBar**: Quick access in top-right corner

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
├── INSTALL.md                   # Installation guide
├── install.py                   # Simple installer
├── MonoStudio_package.json      # Houdini package definition
├── instructions.md              # Development guidelines
├── LICENSE                      # License file
├── python/                      # Python package
│   └── mono_tools/              # Main tools package
├── menus/                       # Houdini menu definitions
├── shelves/                     # Houdini shelf definitions
├── scripts/                     # Startup scripts
├── otls/                        # Houdini OTL files
├── toolbar/                     # Houdini toolbar files
├── config/                      # Configuration files
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
- **Mono Studio** shelf with 4 tools
- Click buttons to launch tools

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

- **v2.0.0** - PySide6 support, clean project structure, professional installer
- **v1.x** - Legacy versions

---

**🎊 Mono Studio - Professional Houdini Tools Package!**
