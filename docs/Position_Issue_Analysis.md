# MiniBar Position Issue Analysis

## 🔍 Vấn Đề

Có **2 vị trí mặc định khác nhau**:

### 1️⃣ `_get_default_position()` (line 542-564)
**Used by:**
- Initial load (no saved position)
- Reset position

**Logic:**
```python
# Relative to PRIMARY SCREEN
screen = QtWidgets.QApplication.primaryScreen()
screen_geo = screen.availableGeometry()

new_x = screen_geo.x() + screen_geo.width() - 400 - 20  # 20px from right edge
new_y = screen_geo.y() + 20                              # 20px from top
```

**Example** (1920x1080 screen):
```
x = 0 + 1920 - 400 - 20 = 1500
y = 0 + 20 = 20
→ Position: (1500, 20) - Top-right of SCREEN
```

---

### 2️⃣ `_snap_top_right()` (line 585-590)
**Used by:**
- User clicks "Snap to Top Right" in menu

**Logic:**
```python
# Relative to HOUDINI WINDOW
mw = hou.qt.mainWindow()
geo = mw.geometry()

new_x = geo.x() + int(0.915 * geo.width()) - self.width()  # 91.5% from left
new_y = geo.y() + int(0.000 * geo.height())                 # At top edge
```

**Example** (Houdini window at x=100, width=1600):
```
x = 100 + int(0.915 * 1600) - 400 = 100 + 1464 - 400 = 1164
y = 100 + 0 = 100
→ Position: (1164, 100) - Inside Houdini window, not screen edge!
```

---

## ❌ Vấn Đề

**Không nhất quán!**

| Action | Reference | Position |
|--------|-----------|----------|
| First load | PRIMARY SCREEN | (1500, 20) |
| Reset | PRIMARY SCREEN | (1500, 20) |
| Snap to Top-Right | HOUDINI WINDOW | (1164, 100) |

→ **Confusing** cho user!

---

## ✅ Giải Pháp

### Option A: All Relative to Screen (Current)
- Default: Screen top-right
- Reset: Screen top-right
- Snap: Screen top-right ← Change this!

### Option B: All Relative to Houdini Window
- Default: Houdini top-right
- Reset: Houdini top-right
- Snap: Houdini top-right

---

## 💡 Recommendation: Option A (Screen-based)

**Lý do:**
1. ✅ Consistent across Houdini sessions
2. ✅ Multi-monitor friendly
3. ✅ More predictable for users
4. ✅ MiniBar always visible (not hidden with Houdini)

**Changes needed:**
- Unify `_snap_top_right()` to use same logic as `_get_default_position()`
- Or rename "Snap to Top Right" → "Snap to Houdini Top Right" (clarify)

