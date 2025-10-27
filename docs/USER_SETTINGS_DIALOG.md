# User Settings Dialog - Implementation

## ✅ Complete

**Feature**: Settings Menu → 👤 User: username → Opens User Settings Dialog  
**Version**: 2.3.0  
**Status**: Ready for Testing

---

## 🎯 Overview

Changed User Info behavior from **display-only message** to **editable dialog**.

### Before:
```
⚙️ Settings Menu → 👤 User: john
  → Shows read-only info message
```

### After:
```
⚙️ Settings Menu → 👤 User: john
  → Opens User Settings Dialog
  → Edit username, full name, email, department
  → Save changes
```

---

## 🎨 User Settings Dialog

### Dialog Layout:

```
┌─────────────────────────────────────┐
│  User Settings                  × │
├─────────────────────────────────────┤
│                                     │
│  Configure your user profile:      │
│                                     │
│  Username:    [john              ] │
│  Lowercase letters, numbers, _ only│
│                                     │
│  Full Name:   [John Smith        ] │
│  Email:       [john@studio.com   ] │
│                                     │
│  First Activity: 2024-12-19        │
│  Last Activity: 2024-12-19         │
│                                     │
│               [Cancel]  [Save]     │
└─────────────────────────────────────┘
```

**Note**: Department field removed to avoid confusion with Department selection in MiniBar.

---

## 📋 Fields

### 1. Username (Required)
**Type**: Text input  
**Validation**: 
- Lowercase letters, numbers, underscore only
- Pattern: `^[a-z0-9_]+$`
- Cannot start with `\d{2}_` (reserved for subdepartments)
- Max 20 characters

**Examples:**
- ✅ `john`, `mary`, `david_nguyen`, `techartist`
- ❌ `John` (uppercase), `01_john` (numeric prefix), `john-work` (dash)

**Behavior:**
- Auto-converts to lowercase on save
- Validates on save
- Shows error if invalid

---

### 2. Full Name (Optional)
**Type**: Text input  
**Format**: Free text (any characters)  
**Example**: `John Smith`, `Mary Johnson`

**Behavior:**
- If empty, defaults to username
- Saved to `.mono/users.json`

---

### 3. Email (Optional)
**Type**: Text input  
**Format**: Free text (no validation)  
**Example**: `john@studio.com`

**Behavior:**
- No email validation (flexible for internal formats)
- Saved to `.mono/users.json`

---

### 4. Department (Optional)
**Type**: Text input  
**Format**: Free text  
**Example**: `Modeling`, `Rigging`, `FX`

**Behavior:**
- Free form (not validated against dept config)
- Saved to `.mono/users.json`

---

### 5. Activity Info (Read-only)
**Display**: 
- First Activity: YYYY-MM-DD
- Last Activity: YYYY-MM-DD

**Behavior:**
- Only shown if user has previous activity
- Not editable
- Loaded from `.mono/users.json`

---

## 💾 Save Behavior

### When clicking "Save":

**1. Validate Username**
```python
# Check pattern
if not re.match(r'^[a-z0-9_]+$', username):
    → Show error: "Username must be lowercase..."
    → Don't save

# Check numeric prefix
if re.match(r'^\d{2}_', username):
    → Show error: "Username cannot start with ##..."
    → Don't save

# Check length
if len(username) > 20:
    → Show error: "Username too long..."
    → Don't save
```

**2. Save to QSettings**
```python
self.s.setValue("user_name", new_username)
self.s.sync()
```

**3. Save to Project Metadata** (if project configured)
```python
# Update .mono/users.json
register_user_activity(
    project_path,
    new_username,
    full_name=full_name,
    email=email,
    department=department
)
```

**4. Update Metadata**
```json
{
  "users": {
    "john": {
      "full_name": "John Smith",         ← Updated
      "email": "john@studio.com",        ← Updated
      "department": "Modeling",          ← Updated
      "created": "2024-12-19T10:30:00",  ← Preserved
      "last_active": "2024-12-19T15:45:00" ← Updated to now
    }
  }
}
```

**5. Show Success Message**
```
User settings saved!

Username: john
```

---

## 🎛️ Settings Menu Flow

### Complete Flow:

```
1. Click ⚙️ Button
   ↓
2. Menu opens:
   ├─ 👤 User: john       ← Click this
   ├─ ───────────
   ├─ ⚙️ Settings
   └─ ℹ️ About
   ↓
3. User Settings Dialog opens
   ↓
4. Edit fields:
   - Username: john
   - Full Name: John Smith
   - Email: john@studio.com
   - Department: Modeling
   ↓
5. Click Save
   ↓
6. Validation:
   - Username valid? → Continue
   - Username invalid? → Show error, stay in dialog
   ↓
7. Save to:
   - QSettings (user_name)
   - .mono/users.json (full profile)
   ↓
8. Show success message
   ↓
9. Close dialog
   ↓
10. Menu shows updated username next time
```

---

## 🔧 Technical Implementation

### File: `python/mono_tools/file_manager/file_manager_minibar.py`

**Method**: `_show_user_info()` (line ~1894-2065)

**Changed from**: Simple info display  
**Changed to**: Full settings dialog

**Key Changes:**

**1. Dialog Creation:**
```python
dialog = QtWidgets.QDialog(self)
dialog.setWindowTitle("User Settings")
dialog.setMinimumWidth(400)
```

**2. Load Current Values:**
```python
current_username = get_current_username()
metadata = load_user_metadata(project_path)
user_info = metadata.get('users', {}).get(current_username, {})
```

**3. Create Form Fields:**
```python
username_edit = QtWidgets.QLineEdit(current_username)
fullname_edit = QtWidgets.QLineEdit(user_info.get('full_name', ''))
email_edit = QtWidgets.QLineEdit(user_info.get('email', ''))
department_edit = QtWidgets.QLineEdit(user_info.get('department', ''))
```

**4. Save Handler:**
```python
def save_user_settings():
    # Get values
    new_username = username_edit.text().strip().lower()
    full_name = fullname_edit.text().strip()
    email = email_edit.text().strip()
    department = department_edit.text().strip()
    
    # Validate
    is_valid, error_msg = validate_username(new_username)
    if not is_valid:
        hou.ui.displayMessage(error_msg, ...)
        return
    
    # Save to QSettings
    self.s.setValue("user_name", new_username)
    
    # Save to metadata
    register_user_activity(project_path, new_username, ...)
    
    # Success
    hou.ui.displayMessage("User settings saved!", ...)
    dialog.accept()
```

---

## 🎨 Styling

**Dialog Style:**
```python
dialog.setStyleSheet("""
    QDialog { background: #2b2b2b; }
    QLabel { color: #e5e5e5; }
    QLineEdit { 
        background: #1e1e1e; 
        color: #e5e5e5; 
        border: 1px solid #3a3a3a; 
        border-radius: 4px; 
        padding: 6px;
    }
    QLineEdit:focus { border: 1px solid #3d5a99; }
    QPushButton {
        background: #3a3a3a;
        color: #e5e5e5;
        border: 1px solid #4a4a4a;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
    }
    QPushButton:hover { background: #4a4a4a; }
    QPushButton:pressed { background: #2a2a2a; }
""")
```

**Consistent with:**
- MiniBar style
- Settings Dialog style
- Other menus

---

## 🧪 Testing Scenarios

### Test 1: First Time User
```
1. Fresh install (no QSettings, no metadata)
2. Click ⚙️ → User: (auto-detected)
3. Dialog opens with:
   - Username: (OS username, lowercased)
   - Other fields: empty
   - Activity info: not shown (no previous activity)
4. Edit fields, click Save
5. Success message shown
6. Check QSettings: user_name saved
7. Check .mono/users.json: user entry created
```

### Test 2: Existing User
```
1. User "john" already configured
2. Click ⚙️ → User: john
3. Dialog opens with:
   - Username: john
   - Full Name: John Smith (from metadata)
   - Email: john@studio.com (from metadata)
   - Department: Modeling (from metadata)
   - Activity info shown
4. Edit fields, click Save
5. Success message shown
6. Metadata updated with new values
7. last_active timestamp updated
```

### Test 3: Username Validation
```
1. Open User Settings Dialog
2. Try invalid usernames:
   - "John" → Error: "must be lowercase"
   - "01_john" → Error: "cannot start with ##"
   - "john-work" → Error: "only letters, numbers, _"
3. Try valid username:
   - "john" → Success
```

### Test 4: No Project Configured
```
1. No project_root in QSettings
2. Click ⚙️ → User: username
3. Dialog opens normally
4. Edit username, click Save
5. Saved to QSettings only (not metadata)
6. Success message shown
7. No .mono/users.json created (no project)
```

### Test 5: Cancel Changes
```
1. Open User Settings Dialog
2. Edit fields
3. Click Cancel
4. Dialog closes
5. No changes saved
6. QSettings unchanged
7. Metadata unchanged
```

---

## 📊 Data Flow

### Save Process:

```
User Input
  ↓
[Username Field] → Validate → lowercase → QSettings
[Full Name Field] ────────────────────→ Metadata
[Email Field] ─────────────────────────→ Metadata
[Department Field] ────────────────────→ Metadata
  ↓
QSettings:
  user_name = "john"
  
.mono/users.json:
  {
    "users": {
      "john": {
        "full_name": "John Smith",
        "email": "john@studio.com",
        "department": "Modeling",
        "created": "2024-12-19T10:30:00",
        "last_active": "2024-12-19T15:45:00"
      }
    }
  }
```

---

## 🎯 Benefits

### 1. User-Friendly
- Easy to edit profile
- Visual feedback
- Clear validation errors

### 2. Flexible
- Works with or without project
- Optional fields
- Free-form department

### 3. Consistent
- Same style as other dialogs
- Same validation logic
- Same save behavior

### 4. Trackable
- Activity timestamps preserved
- Full history in metadata
- Easy to identify users

---

## 🔮 Future Enhancements

### Phase 2 (Optional):
1. **Avatar Upload** - Profile picture
2. **Department Dropdown** - Select from config departments
3. **Email Validation** - Check format
4. **Username History** - Track username changes
5. **Multi-Project Sync** - Sync profile across projects

---

## ✅ Implementation Complete

**Files Modified:**
- `python/mono_tools/file_manager/file_manager_minibar.py`
  - Updated `_show_user_info()` to show dialog instead of message

**Features:**
- ✅ User Settings Dialog
- ✅ Username validation
- ✅ Save to QSettings
- ✅ Save to metadata
- ✅ Activity tracking
- ✅ Error handling
- ✅ Consistent styling

**Ready for Testing!** 🚀

---

**Usage:**
```python
# In Houdini:
from mono_tools import show_mono_minibar
show_mono_minibar()

# Click ⚙️ button
# Click "👤 User: username"
# Edit profile
# Click Save
```

---

**Questions?**  
Check main documentation or contact development team.

**© 2024 MonoStudio**

