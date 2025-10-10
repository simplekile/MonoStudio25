# Startup.py - Flow Explanation

## 📋 File: `scripts/startup.py` (45 dòng)

### 🎯 Mục Đích
Script này được Houdini tự động gọi khi load package, dùng để khởi tạo Mono Studio.

---

## 🔄 Execution Flow

### 1️⃣ **Houdini Starts** → **Load Package**
```
Houdini khởi động
   ↓
Đọc $HOUDINI_PACKAGE_DIR/MonoStudio25.json
   ↓
Set environment variables (MONO_STUDIO, PYTHONPATH, etc.)
   ↓
Tìm "script": ["$MONO_STUDIO/scripts/startup.py"]
   ↓
Execute startup.py  ← BẮT ĐẦU TỪ ĐÂY
```

### 2️⃣ **Import Phase** (Line 6-7)
```python
import hou                     # Houdini API
from mono_tools.qt import QtCore  # Qt for timer
```

**Chạy ngay lập tức** khi Python load file.

**Vì sao cần QtCore?**
→ Để dùng `QTimer.singleShot()` cho delayed execution

---

### 3️⃣ **Print Welcome** (Line 9)
```python
print("🚀 Mono Studio v2.2.0 - Loading...")
```

**Output trong Houdini console** ngay khi script chạy.

---

### 4️⃣ **Setup Menus** (Line 12-28)
```python
try:
    from mono_tools import (
        setup_file_manager_tools,    # Add File Manager to menu
        setup_material_loader_tools, # Add Material Loader to menu
        setup_texture_tools,         # Add Texture Tools to menu
        show_mono_minibar            # Import for later use
    )
    
    setup_file_manager_tools()    # Execute: create menu items
    setup_material_loader_tools() # Execute: create menu items
    setup_texture_tools()         # Execute: create menu items
    print("✅ Menus loaded!")
    
except Exception as e:
    print(f"❌ Menu setup failed: {e}")
    traceback.print_exc()
```

#### 🔍 Chi Tiết:
**Line 13-18**: Import các functions từ `mono_tools`
- `PYTHONPATH` đã được set trong package.json → import thành công

**Line 20-22**: Gọi từng setup function
- Mỗi function tạo menu items trong Houdini menu bar
- Ví dụ: "Mono Studio" → "File Manager", "Material Loader", etc.

**Line 23**: In success message

**Line 25-28**: Error handling
- Nếu import hoặc setup fail → print error + traceback
- **Không crash Houdini**, chỉ báo lỗi

---

### 5️⃣ **Define Delayed Function** (Line 31-42)
```python
def delayed_minibar_show():
    try:
        minibar = show_mono_minibar()  # Create & show MiniBar widget
        if minibar:
            print("✅ MiniBar ready!")
            print("🎉 Mono Studio ready!")
        else:
            print("⚠️ MiniBar creation failed")
    except Exception as e:
        print(f"❌ MiniBar error: {e}")
        traceback.print_exc()
```

**Lưu ý**: Function này **CHƯA** được gọi ngay!
- Chỉ **define** function
- Sẽ được gọi sau bởi timer

#### 🔍 Chi Tiết:
**Line 33**: `show_mono_minibar()` 
- Tạo widget MiniBar
- Show nó lên màn hình
- Return minibar object

**Line 34-37**: Success handling
- Nếu minibar tạo thành công → print messages

**Line 39-42**: Error handling
- Nếu fail → print error với full traceback

---

### 6️⃣ **Schedule Delayed Execution** (Line 45)
```python
QtCore.QTimer.singleShot(500, delayed_minibar_show)
```

#### 🎯 Đây là KEY!

**`QTimer.singleShot(milliseconds, function)`**
- Chờ 500ms
- Sau đó gọi `delayed_minibar_show()`
- **Non-blocking**: Script tiếp tục chạy, không đợi

**Vì sao cần delay 500ms?**
```
t=0ms:   Script chạy xong → return control về Houdini
t=0-500ms: Houdini tiếp tục khởi tạo UI, load panels, etc.
t=500ms: Timer trigger → gọi delayed_minibar_show()
         → MiniBar xuất hiện
```

**Nếu không delay sẽ sao?**
→ MiniBar có thể được tạo **trước khi Houdini UI sẵn sàng**
→ Qt parent window chưa có → crash hoặc không hiển thị

---

## 📊 Timeline Diagram

```
Time | Action                           | Where
-----|----------------------------------|------------------
0ms  | Houdini loads package           | Houdini Core
1ms  | Execute startup.py              | Python Interpreter
2ms  | Import hou, QtCore              | Python
3ms  | Print "Loading..."              | Houdini Console
5ms  | Import mono_tools functions     | Python
10ms | setup_file_manager_tools()      | Menu System
15ms | setup_material_loader_tools()   | Menu System
20ms | setup_texture_tools()           | Menu System
25ms | Print "Menus loaded!"           | Houdini Console
30ms | Define delayed_minibar_show()   | Python (just define)
35ms | QTimer.singleShot(500, ...)     | Qt Event Loop (schedule)
40ms | Script DONE → return            | Back to Houdini
...  | Houdini continues loading UI    | Houdini Core
500ms| Timer fires!                    | Qt Event Loop
501ms| Call delayed_minibar_show()     | Python
505ms| show_mono_minibar()             | Create Widget
510ms| MiniBar appears!                | Houdini UI
515ms| Print "MiniBar ready!"          | Houdini Console
520ms| Print "Mono Studio ready!"      | Houdini Console
```

---

## 🎯 Key Concepts

### 1. **Non-Blocking Startup**
```python
# ❌ BAD - Blocks Houdini
show_mono_minibar()  # Wait for user interaction
print("Done")        # Never reached if dialog blocks

# ✅ GOOD - Non-blocking
QTimer.singleShot(500, show_mono_minibar)
print("Done")  # Reached immediately, minibar shows later
```

### 2. **Why 500ms?**
- Too short (100ms): UI might not be ready
- Too long (2000ms): User waits unnecessarily
- 500ms: Sweet spot - UI usually ready, not too slow

### 3. **Error Handling**
```python
try:
    # Setup code
except Exception as e:
    print(error)
    traceback.print_exc()  # Full stack trace
    # Continue (don't crash Houdini)
```

**Philosophy**: Better to show error than crash entire application

### 4. **Import Strategy**
```python
# Import at usage time, not top of file
def delayed_minibar_show():
    # show_mono_minibar already imported at line 17
    minibar = show_mono_minibar()
```

Imports done early → faster execution when timer fires

---

## 🔍 What Each Function Does

### `setup_file_manager_tools()`
**File**: `python/mono_tools/file_manager/file_manager_menu_integration.py`

Creates menu items:
- "Mono Studio" → "File Manager"
- "Mono Studio" → "MiniBar"

### `setup_material_loader_tools()`
**File**: `python/mono_tools/material_loader/material_loader_menu_integration.py`

Creates menu item:
- "Mono Studio" → "Material Loader"

### `setup_texture_tools()`
**File**: `python/mono_tools/texture_search_replace/texture_menu_integration.py`

Creates menu item:
- "Mono Studio" → "Texture Search & Replace"

### `show_mono_minibar()`
**File**: `python/mono_tools/file_manager/file_manager_api.py`

1. Check if MiniBar already exists (singleton pattern)
2. If not, create new `MonoFileMiniBar` widget
3. Position it on screen
4. Show it
5. Return the widget

---

## 🧪 Testing Flow

### Test 1: Print Statements
```python
# In Houdini console, check output:
🚀 Mono Studio v2.2.0 - Loading...
✅ Menus loaded!
✅ MiniBar ready!
🎉 Mono Studio ready!
```

### Test 2: Menu Items
Check menu bar:
```
Mono Studio ▼
  ├─ File Manager
  ├─ MiniBar
  ├─ Material Loader
  └─ Texture Search & Replace
```

### Test 3: MiniBar Widget
Look for floating widget with:
- ⋮⋮ handle
- 🏷️ Type button
- 📁 Dept button
- Shot display
- ⚡💾⚙️ buttons

---

## ⚡ Performance

### Startup Time
- **Import + Setup**: ~30-50ms
- **Script completion**: ~40ms
- **MiniBar creation**: ~10-20ms (after 500ms)
- **Total user-perceived time**: ~500-520ms

### Memory
- **Script**: ~1-2MB (Python modules)
- **MiniBar widget**: ~5-10MB (Qt widgets)
- **Total overhead**: Negligible for modern systems

---

## 🐛 Common Issues

### Issue 1: MiniBar doesn't show
**Possible causes:**
- Houdini UI not ready (increase delay)
- Import errors (check console)
- Qt parent window issue

**Debug:**
```python
# Check if function was called
print("delayed_minibar_show called")  # Add to line 32
```

### Issue 2: Menu items missing
**Possible causes:**
- Import failed (check traceback)
- Menu integration function error

**Debug:**
```python
# Check each setup separately
setup_file_manager_tools()  # Should print something
```

### Issue 3: Slow startup
**Possible causes:**
- Delay too long (reduce from 500ms)
- Heavy imports (optimize)

**Measure:**
```python
import time
start = time.time()
# ... code ...
print(f"Took {time.time()-start:.2f}s")
```

---

## 💡 Design Decisions

### Why separate delayed function?
```python
# Could do this:
QTimer.singleShot(500, lambda: show_mono_minibar())

# But we do this:
def delayed_minibar_show():
    # ... with error handling ...
QTimer.singleShot(500, delayed_minibar_show)
```

**Reason**: Better error handling, debugging, and logging

### Why not auto-import everything?
```python
# Could import at top
from mono_tools import *

# But we explicitly import
from mono_tools import setup_file_manager_tools, ...
```

**Reason**: Clear dependencies, avoid namespace pollution

### Why try-except around everything?
**Philosophy**: Package loading should never crash Houdini
→ Better to have partial functionality than no Houdini

---

## 📚 Related Files

1. **MonoStudio_package.json**: Triggers this script
2. **python/mono_tools/__init__.py**: Exports setup functions
3. **python/mono_tools/file_manager/file_manager_api.py**: MiniBar creation
4. **python/mono_tools/*/menu_integration.py**: Menu setup logic

---

**Last Updated**: 2024-12-19
**Version**: 2.2.0
**Total Lines**: 45 (down from 200+!)

