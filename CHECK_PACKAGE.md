# Check Active Package

## Issue

Houdini đang load version CŨ (MonoStudio) thay vì version MỚI (MonoStudio25)

Evidence:
```
📁 Added python path: d:/Dropbox/Stock/Plugin/HOU/MonoStudio\python
                                           ^^^^^^^^^^^
                                           Should be: MonoStudio25
```

---

## Solution

### Check Package Files

**Location:** `C:/Users/[USER]/Documents/houdini21.0/packages/`

**Files to check:**
- MonoStudio.json (OLD - disable this!)
- MonoStudio25.json (NEW - should be active)

### Fix

**Option 1: Rename old package**
```
MonoStudio.json → MonoStudio.json.disabled
```

**Option 2: Delete old package**
```
Delete MonoStudio.json
```

**Option 3: Update MONO_STUDIO path in old package**
```json
{
  "env": [
    {"MONO_STUDIO": "D:/Dropbox/Stock/Plugin/HOU/MonoStudio25"}
  ]
}
```

---

## After Fix

Restart Houdini → Should see:
```
(no prints - silent startup)
MiniBar appears
No debug position messages
```

---

## Also Fix: Legacy Prints

File: `python/mono_tools/file_manager/file_manager.py`
Lines: 599, 1146, 1153

These have hardcoded prints - need to change to debug_print()

