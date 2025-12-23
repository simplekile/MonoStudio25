# -*- coding: utf-8 -*-
"""
Demo: Quá trình tạo file Asset (không phải Shot)
Minh họa cách New File hoạt động cho asset files

Chạy script này trong Houdini Python Shell để xem demo
"""

import os
import sys
import re

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Try to import from mono_tools, fallback to local implementations
try:
    from mono_tools.file_manager.file_manager_helpers import (
        clean_type_name,
        clean_asset_name,
        clean_department_name,
        generate_new_filename,
        get_current_username
    )
except ImportError:
    # Fallback implementations if not running in Houdini
    def clean_type_name(type_name):
        """Clean type name: remove underscore prefix"""
        if not type_name:
            return ""
        return type_name.lstrip('_')
    
    def clean_asset_name(asset_name):
        """Clean asset name: remove prefix like char_, prop_, env_"""
        if not asset_name:
            return ""
        prefixes = ['char_', 'prop_', 'env_', 'veh_', 'fx_', 'graphic_']
        for prefix in prefixes:
            if asset_name.lower().startswith(prefix):
                return asset_name[len(prefix):]
        return asset_name
    
    def clean_department_name(dept_name):
        """Clean department name: remove number prefix"""
        if not dept_name:
            return ""
        cleaned = re.sub(r'^\d+_', '', dept_name)
        return cleaned
    
    def generate_new_filename(type_name, asset_name, department, version="v001", ext=".hip"):
        """Generate filename in format: $type_$assetname_$department_$version.ext"""
        clean_type = clean_type_name(type_name)
        clean_asset = clean_asset_name(asset_name)
        clean_dept = clean_department_name(department)
        
        if not version.startswith('v'):
            version = f"v{version}"
        if not ext.startswith('.'):
            ext = f".{ext}"
        
        filename = f"{clean_type}_{clean_asset}_{clean_dept}_{version}{ext}"
        return filename
    
    def get_current_username():
        """Get current username - fallback to system username"""
        import getpass
        return getpass.getuser().lower()


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_new_file_asset():
    """Demo quá trình tạo file asset (không phải shot)"""
    
    print_section("DEMO: QUÁ TRÌNH TẠO FILE ASSET (KHÔNG PHẢI SHOT)")
    
    # ============================================================
    # BƯỚC 1: User Selection trong MiniBar
    # ============================================================
    print_section("BƯỚC 1: User Selection trong MiniBar")
    
    print("""
    User click vào MiniBar và chọn:
    """)
    
    # Simulate user selections
    type_name = "_characters"  # User chọn từ Type dropdown
    department = "01_modeling"  # User chọn từ Department dropdown
    subdepartment = None  # Có thể có hoặc không
    asset_name_input = "Cyborg"  # User nhập vào dialog
    
    print(f"  🏷️  Type: {type_name}")
    print(f"  📁 Department: {department}")
    print(f"  📂 Subdepartment: {subdepartment or '(None)'}")
    print(f"  ✏️  Asset Name (user input): {asset_name_input}")
    
    # ============================================================
    # BƯỚC 2: Auto-detect Username
    # ============================================================
    print_section("BƯỚC 2: Auto-detect Username")
    
    try:
        username = get_current_username()
        print(f"  👤 Username (auto-detected): {username}")
    except:
        username = "john"  # Fallback
        print(f"  👤 Username (fallback): {username}")
    
    # ============================================================
    # BƯỚC 3: Name Cleaning Process
    # ============================================================
    print_section("BƯỚC 3: Name Cleaning Process")
    
    print("\n  3.1. Clean Type Name:")
    print(f"      Input:  {type_name}")
    clean_type = clean_type_name(type_name)
    print(f"      Output: {clean_type}")
    print(f"      Rule: Remove underscore prefix (_)")
    
    print("\n  3.2. Clean Asset Name:")
    # Add prefix if needed (code logic)
    asset_name_with_prefix = asset_name_input
    if not any(asset_name_input.lower().startswith(p) for p in ['char_', 'prop_', 'env_', 'veh_']):
        if 'character' in type_name.lower():
            asset_name_with_prefix = f"char_{asset_name_input}"
        elif 'prop' in type_name.lower():
            asset_name_with_prefix = f"prop_{asset_name_input}"
        elif 'environment' in type_name.lower():
            asset_name_with_prefix = f"env_{asset_name_input}"
    
    print(f"      Input:  {asset_name_input}")
    print(f"      With prefix: {asset_name_with_prefix}")
    clean_asset = clean_asset_name(asset_name_with_prefix)
    print(f"      Output: {clean_asset}")
    print(f"      Rule: Remove prefix (char_, prop_, env_, etc.)")
    
    print("\n  3.3. Clean Department Name:")
    print(f"      Input:  {department}")
    clean_dept = clean_department_name(department)
    print(f"      Output: {clean_dept}")
    print(f"      Rule: Remove number prefix (01_, 02_, etc.)")
    
    # ============================================================
    # BƯỚC 4: Generate Filename
    # ============================================================
    print_section("BƯỚC 4: Generate Filename")
    
    print("\n  Format: $type_$assetname_$department_$version.ext")
    print("\n  Components:")
    print(f"    - Type:     {clean_type}")
    print(f"    - Asset:    {clean_asset}")
    print(f"    - Dept:     {clean_dept}")
    print(f"    - Version:  v001")
    print(f"    - Ext:      .hip")
    
    filename = generate_new_filename(
        type_name=type_name,
        asset_name=asset_name_with_prefix,
        department=department,
        version="v001",
        ext=".hip"
    )
    
    print(f"\n  ✅ Generated Filename: {filename}")
    
    # ============================================================
    # BƯỚC 5: Build Folder Structure
    # ============================================================
    print_section("BƯỚC 5: Build Folder Structure")
    
    print("\n  Asset File Structure:")
    print("    01_assets/{type}/{asset}/{dept}/[{subdept}/]{user}/")
    
    path_parts = [
        "01_assets",
        type_name,
        asset_name_with_prefix,
        department
    ]
    
    if subdepartment:
        path_parts.append(subdepartment)
        print(f"\n  Path parts: {path_parts}")
        print(f"  + Subdepartment: {subdepartment}")
    
    path_parts.append(username)
    print(f"\n  Path parts: {path_parts}")
    print(f"  + User workspace: {username}")
    
    target_dir = os.path.join(*path_parts)
    print(f"\n  ✅ Target Directory: {target_dir}")
    
    # ============================================================
    # BƯỚC 6: Full File Path
    # ============================================================
    print_section("BƯỚC 6: Full File Path")
    
    filepath = os.path.join(target_dir, filename)
    print(f"  ✅ Full File Path: {filepath}")
    
    # ============================================================
    # BƯỚC 7: Process Summary
    # ============================================================
    print_section("QUÁ TRÌNH HOÀN CHỈNH")
    
    print("""
  📋 TÓM TẮT QUÁ TRÌNH:
  
  1. User chọn Type & Department trong MiniBar
  2. User click button "📄 New File"
  3. Dialog NewFileDialog mở với:
     - Type: auto-filled từ selection
     - Department: auto-filled từ selection
     - Subdepartment: từ selection (nếu có)
     - Username: auto-detected
     - Asset Name: user nhập
  
  4. User nhập tên asset (ví dụ: "Cyborg")
  5. Dialog preview path real-time
  
  6. User click "Create File"
  7. Code thực hiện:
     a. Validate tất cả fields
     b. Clean names (type, asset, dept)
     c. Generate filename theo format
     d. Build folder path
     e. Create folder structure nếu chưa có
     f. Check file exists → hỏi mở nếu có
     g. Check unsaved changes → hỏi save
     h. Clear scene: hou.hipFile.clear()
     i. Save file: hou.hipFile.save(filepath)
     j. Register user activity
     k. Refresh file list
     l. Show success message
  
  8. File được tạo và mở trong Houdini
  9. MiniBar tự động refresh để hiển thị file mới
  """)
    
    # ============================================================
    # COMPARISON: Asset vs Shot
    # ============================================================
    print_section("SO SÁNH: Asset File vs Shot File")
    
    print("\n  📁 ASSET FILE:")
    print(f"     Type: {type_name}")
    print(f"     Structure: 01_assets/{type_name}/{asset_name_with_prefix}/{department}/[{subdepartment}/]{username}/")
    print(f"     Filename: {filename}")
    print(f"     Format: {clean_type}_{clean_asset}_{clean_dept}_v001.hip")
    
    print("\n  🎬 SHOT FILE:")
    print(f"     Type: Shots")
    print(f"     Structure: 02_shots/{department}/[{subdepartment}/]{username}/")
    print(f"     Filename: Shots_Sh010_{clean_dept}_v001.hip")
    print(f"     Format: Shots_{{shot_name}}_{{dept}}_{{version}}.hip")
    
    print("\n  🔑 KHÁC BIỆT:")
    print("     - Asset: Có folder riêng cho từng asset (char_Cyborg/)")
    print("     - Shot: Tất cả shots trong cùng folder department")
    print("     - Asset: Filename bao gồm type + asset name")
    print("     - Shot: Filename chỉ có type (Shots) + shot number")
    
    # ============================================================
    # EXAMPLE WORKFLOW
    # ============================================================
    print_section("VÍ DỤ WORKFLOW HOÀN CHỈNH")
    
    print("""
  🎯 Scenario: Tạo file modeling cho character "Cyborg"
  
  Step 1: User làm việc trong MiniBar
    - MiniBar hiển thị: 🏷️ Type | 📁 Dept
    - User click 🏷️ → chọn "_characters"
    - User click 📁 → chọn "01_modeling"
  
  Step 2: User click button "📄 New File"
    - Dialog mở với các field đã auto-filled
  
  Step 3: User nhập thông tin
    - Type: _characters (đã chọn)
    - Department: 01_modeling (đã chọn)
    - Subdepartment: (None) hoặc chọn từ dropdown
    - User: john (auto-detected)
    - Asset Name: Cyborg (user nhập)
  
  Step 4: Dialog preview
    - Preview shows: 01_assets/_characters/char_Cyborg/01_modeling/john/characters_Cyborg_modeling_v001.hip
  
  Step 5: User click "Create File"
    - Code tạo folder: 01_assets/_characters/char_Cyborg/01_modeling/john/
    - Code tạo file: characters_Cyborg_modeling_v001.hip
    - File mở trong Houdini
  
  Step 6: File ready để làm việc
    - Scene đã clear (blank scene)
    - File đã save
    - User có thể bắt đầu modeling
  """)
    
    print("\n" + "=" * 70)
    print("  ✅ DEMO HOÀN TẤT")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    demo_new_file_asset()

