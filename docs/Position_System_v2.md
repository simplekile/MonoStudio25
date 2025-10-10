# MiniBar Position System v2.0 (Simplified)

## Overview

Simplified positioning system from **150 lines** to **~70 lines** while keeping smart follow-Houdini behavior.

---

## How It Works

### Single Source of Truth: Offset

```python
# Only 2 values stored:
minibar_offset_x = -85  # Distance from Houdini right edge
minibar_offset_y = 0    # Distance from Houdini top edge
```

### Position Calculation

```python
# When Houdini is at (100, 50) with size 1600x900:
hou_right = 100 + 1600 = 1700
hou_top = 50

minibar_right = 1700 + (-85) = 1615
minibar_top = 50 + 0 = 50

minibar_x = 1615 - minibar_width = 1615 - 400 = 1215
minibar_y = 50

→ MiniBar at (1215, 50)
```

---

## Features

### 1. Persistent Position (Saved Across Restarts)
```
Session 1: User drags MiniBar
  → Calculate offset: (-85, 0)
  → Save to QSettings

Session 2: Restart Houdini
  → Load offset: (-85, 0)
  → Apply to current Houdini geometry
  → MiniBar appears at same relative position ✅
```

### 2. Follow Houdini Window
```
User resizes Houdini window:
  → Event filter detects change (150ms debounce)
  → Recalculate position using saved offset
  → MiniBar follows window ✅
```

### 3. Multi-Monitor Support
```
Offset-based → Works on any screen size
Move Houdini to different monitor → MiniBar follows ✅
```

---

## API

### Save Position
```python
# Called after:
- Drag & drop (mouse release)
- Close MiniBar

minibar._save_relative_position()
```

### Restore Position
```python
# Called during:
- __init__ (startup)

minibar._restore_relative_position()
```

### Reset Position
```python
# Right-click menu → "Reset Position"
# Sets offset to default (-85, 0)

minibar._reset_position()
```

### Update Position
```python
# Called when:
- Houdini window resize/move
- Reset position
- Restore position

minibar._update_position_relative_to_main_window()
```

---

## Code Comparison

### Before (Complex - 150 lines)

**Storage:** 8 values
```python
minibar_x, minibar_y              # Absolute
minibar_offset_x, minibar_offset_y  # Offset
minibar_rel_x, minibar_rel_y       # Relative (0.0-1.0)
minibar_abs_x, minibar_abs_y       # Duplicate
```

**Features:**
- Threshold checks (>5px to save)
- Stability counter (3 frames)
- Range validation (0.85-1.05)
- Distance calculations
- Multiple position formats

**Problems:**
- Complex logic
- Hard to debug
- Redundant storage
- Performance overhead

---

### After (Simple - 70 lines)

**Storage:** 2 values
```python
minibar_offset_x  # Offset from Houdini right edge
minibar_offset_y  # Offset from Houdini top edge
```

**Features:**
- Clean offset calculation
- 150ms debounce (event filter)
- Screen bounds validation
- Always save (no threshold)

**Benefits:**
- Simple logic
- Easy to debug
- Minimal storage
- Faster execution

---

## Functions

### _save_relative_position() (15 lines)
```python
def _save_relative_position(self):
    """Save MiniBar position as offset from Houdini window"""
    # 1. Get Houdini geometry
    # 2. Calculate offset from right/top edges
    # 3. Save to QSettings
```

### _update_position_relative_to_main_window() (25 lines)
```python
def _update_position_relative_to_main_window(self):
    """Update position when Houdini window changes"""
    # 1. Load saved offset
    # 2. Calculate new position from Houdini geometry + offset
    # 3. Validate screen bounds
    # 4. Move to new position
```

### _restore_relative_position() (5 lines)
```python
def _restore_relative_position(self):
    """Restore position at startup"""
    # Simply call _update_position_relative_to_main_window()
    # Uses saved offset (or default -85, 0)
```

### _reset_position() (5 lines)
```python
def _reset_position(self):
    """Reset to default top-right position"""
    # 1. Set offset to default (-85, 0)
    # 2. Apply position
```

### MainWindowEventFilter (15 lines)
```python
class MainWindowEventFilter(QtCore.QObject):
    """Monitor Houdini window changes"""
    # 1. Detect resize/move events
    # 2. Debounce with 150ms timer
    # 3. Update minibar position
```

---

## Default Position

```python
offset_x = -85  # ~20px from Houdini right edge
offset_y = 0    # At Houdini top edge
```

**Visual:**
```
┌─────────────────────────────────┐
│ Houdini Main Window             │
│                       ┌────────┐│ ← 20px from right
│                       │MiniBar ││
│                       └────────┘│
│                                 │
└─────────────────────────────────┘
     ↑ offset_x = -85 (negative = left from right edge)
     ↑ offset_y = 0 (at top)
```

---

## Removed Complexity

### Deleted Code:
- ❌ _position_stable_count counter
- ❌ _last_stable_pos tracking
- ❌ 3-frame stability check
- ❌ Threshold validation (>5px)
- ❌ Relative position (0.0-1.0) calculations
- ❌ Absolute position storage
- ❌ Range checks (0.85-1.05)
- ❌ Distance moved calculations

### Kept Essentials:
- ✅ Offset storage (2 values)
- ✅ Debounce timer (150ms)
- ✅ Screen bounds validation
- ✅ Follow Houdini window
- ✅ Drag & drop
- ✅ Lock/unlock

---

## Performance

### Before:
```
Save: Check threshold → Calculate 3 formats → Save 8 values
Update: Check stability → 3-frame delay → Range validation → Move
```

### After:
```
Save: Calculate offset → Save 2 values
Update: Load offset → Calculate position → Move
```

**Result:** Faster, simpler, more reliable!

---

## Migration

### Old Saved Values (Ignored):
```
minibar_x, minibar_y         → Not used
minibar_rel_x, minibar_rel_y → Not used
minibar_abs_x, minibar_abs_y → Not used
```

### New Values (Used):
```
minibar_offset_x → Loaded and used
minibar_offset_y → Loaded and used
```

**Backward compatible:** If old values exist, they're ignored. Offset defaults to (-85, 0) if not found.

---

**Version:** 2.2.0
**Last Updated:** 2024-12-19
**Status:** Production Ready

