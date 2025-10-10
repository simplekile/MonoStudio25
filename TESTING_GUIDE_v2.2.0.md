# Testing Guide - Mono Studio v2.2.0

## 🚀 Quick Start

### 1. Restart Houdini
```
Close Houdini completely
→ Reopen Houdini
```

### 2. Check Startup (Should be SILENT)
```
✅ No console messages (unless error)
✅ MiniBar appears automatically
✅ Menu "MonoStudio" exists in menu bar
```

---

## ✅ Test Checklist

### Startup Tests

- [ ] **Silent Startup**
  - No console spam
  - MiniBar appears after ~500ms
  - No errors in console

- [ ] **Menu Integration**
  - Menu bar has "MonoStudio" menu
  - 5 menu items present:
    - ⚡ File Manager
    - 🚀 Show MiniBar
    - ❌ Hide MiniBar
    - 🎨 Material Loader
    - 🔍 Texture Search & Replace

### MiniBar Tests

- [ ] **UI Layout (Minimal - 3 buttons)**
  ```
  ⋮⋮ | 🏷️ Type | 📁 Dept | [Shot Display] | ⚡ | ⚙️
  ```
  - Only 3 buttons (not 5!)
  - Clean and compact

- [ ] **Quick Menu (⚡)**
  - Click ⚡ → Menu shows
  - 8 items in correct order:
    1. 📄 New File...
    2. 📁 New Folder...
    3. 💾 Save Version...
    4. ─────────
    5. 📂 Open File Location
    6. 🎬 Open Render Folder
    7. ─────────
    8. 🔄 Reload Scene
    9. 🔃 Restart Houdini

- [ ] **Position System**
  - Drag MiniBar → saves position
  - Restart Houdini → position restored
  - Right-click handle → Reset Position → top-right
  - Resize Houdini → MiniBar follows
  - **No console spam during position changes!**

- [ ] **Context Menu (Right-click handle)**
  - Opens instantly (no lag!)
  - Shows version (v2.2.0)
  - Lock/Unlock works
  - Reset Position works

### New Features Tests

- [ ] **New File (⚡ → 📄 New File...)**
  1. Select Type + Department
  2. Click ⚡ → New File
  3. Enter name: "TestAsset"
  4. Check filename: `characters_TestAsset_modeling_v001.hip`
  5. Check folder created
  6. File opens in Houdini

- [ ] **New Folder (⚡ → 📁 New Folder...)**
  1. Click ⚡ → New Folder
  2. Enter type: `_characters`
  3. Enter name: "TestChar"
  4. Preview shows 7 departments
  5. Confirm → All folders created
  6. Option to create file appears

- [ ] **Save Version (⚡ → 💾 Save Version...)**
  1. Open a file
  2. Click ⚡ → Save Version
  3. Enter note (optional)
  4. Version incremented (v001 → v002)
  5. Old version moved to Vers/ folder

### Debug Mode Tests

- [ ] **Debug Off (Default)**
  ```python
  # In Houdini console - should be silent
  from mono_tools import show_mono_minibar
  show_mono_minibar()
  # No debug prints!
  ```

- [ ] **Debug On**
  ```python
  import os
  os.environ['MONO_DEBUG'] = '1'
  
  # Restart MiniBar or reload modules
  # Should see debug prints
  ```

---

## 🐛 Common Issues & Solutions

### Issue: MiniBar doesn't appear
**Check:**
```python
import os
print(os.environ.get('MONO_STUDIO'))
# Should print: D:/Dropbox/Stock/Plugin/HOU/MonoStudio25
```

**Solution:** Package not loaded, check package file

### Issue: Menu items missing
**Check:** Look for errors in console

**Solution:** Menu integration might have failed silently

### Issue: Position not saved
**Check:**
```python
from mono_tools.qt import QtCore
s = QtCore.QSettings("Mono", "FileManager")
print(s.value("minibar_offset_x"))
print(s.value("minibar_offset_y"))
```

**Solution:** Should print numbers (e.g., -85, 0)

### Issue: New File doesn't work
**Check:** Type + Department selected?

**Solution:** Select both before clicking New File

---

## 📊 Performance Benchmarks

### Expected Performance

| Action | Time | Status |
|--------|------|--------|
| Houdini startup | ~30s | N/A |
| MiniBar appears | +0.5s | ✅ |
| Menu open | <1ms | ✅ |
| Context menu | <1ms | ✅ |
| New File dialog | <50ms | ✅ |
| Position save | <5ms | ✅ |
| Debug mode toggle | Instant | ✅ |

### Red Flags
- ❌ Context menu takes >200ms
- ❌ MiniBar doesn't appear
- ❌ Console spam on startup
- ❌ Position not restored

---

## 🧪 Advanced Testing

### Test Department Config
```python
# Check config loads
from mono_tools.file_manager.file_manager_helpers import get_standard_departments
depts = get_standard_departments()
print(depts)
# Should print 7 departments
```

### Test Auto-Naming
```python
from mono_tools.file_manager.file_manager_helpers import generate_new_filename

filename = generate_new_filename("_characters", "Omega", "01_modeling")
print(filename)
# Should print: characters_Omega_modeling_v001.hip
```

### Test Clean Functions
```python
from mono_tools.file_manager.file_manager_helpers import (
    clean_type_name, 
    clean_department_name, 
    clean_asset_name
)

print(clean_type_name("_characters"))      # → characters
print(clean_department_name("01_modeling")) # → modeling
print(clean_asset_name("char_Cyborg"))     # → Cyborg
```

---

## 📝 Report Template

**If you find bugs, report with:**

```
Bug: [Short description]

Steps to reproduce:
1. 
2. 
3. 

Expected: 
Actual: 

Console output:
[Paste any errors]

Environment:
- Houdini version: 
- OS: Windows 10
- MonoStudio version: 2.2.0
```

---

## ✅ Success Criteria

### Must Work
- ✅ Silent startup
- ✅ Menu appears
- ✅ MiniBar appears
- ✅ Position saves/restores
- ✅ Quick Menu works

### Should Work
- ✅ New File creates correctly
- ✅ New Folder creates structure
- ✅ Save Version increments
- ✅ Debug mode toggles

### Nice to Have
- ✅ No lag anywhere
- ✅ Clean console
- ✅ Smooth animations

---

## 🎉 If All Tests Pass

**Ready for production!**

Next steps:
- Tag release: `git tag v2.2.0`
- Push to remote: `git push --tags`
- Distribute to team
- Celebrate! 🎉

---

**Version:** 2.2.0
**Test Date:** 2024-12-19
**Status:** Ready for Testing

