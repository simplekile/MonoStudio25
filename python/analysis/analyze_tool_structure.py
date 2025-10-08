"""
Script phân tích cấu trúc tool và đưa ra khuyến nghị về folder
"""

import os
import re
from collections import defaultdict

def analyze_tool_structure():
    """Phân tích cấu trúc tool hiện tại"""
    print("Analyzing Mono Studio Tool Structure")
    print("=" * 60)
    
    mono_tools_path = "python/mono_tools"
    
    # Phân loại files theo tool
    tool_files = defaultdict(list)
    standalone_files = []
    
    for filename in os.listdir(mono_tools_path):
        if filename.endswith('.py') and not filename.startswith('__'):
            # Bỏ qua test_demo folder
            if filename in ['test_pyside6.py', 'verify_pyside6.py', 'test_texture_search_replace.py', 
                           'demo_texture_search_replace.py', 'quick_test_pyside6.py']:
                continue
                
            # Phân loại theo pattern
            if filename.startswith('fm_'):
                tool_files['file_manager'].append(filename)
            elif filename.startswith('texture_'):
                tool_files['texture_search_replace'].append(filename)
            elif filename.startswith('material_'):
                tool_files['material_loader'].append(filename)
            elif filename in ['qt.py', 'utils.py']:
                standalone_files.append(filename)
            else:
                # Tìm tool name từ filename
                tool_name = filename.replace('.py', '').replace('_menu_integration', '')
                tool_files[tool_name].append(filename)
    
    # Hiển thị kết quả phân tích
    print("\nTool Analysis Results:")
    print("-" * 40)
    
    for tool_name, files in tool_files.items():
        file_count = len(files)
        print(f"\n🔧 {tool_name.upper()}:")
        print(f"   Files: {file_count}")
        for file in files:
            print(f"   ├── {file}")
        
        # Đưa ra khuyến nghị
        if file_count >= 4:
            print(f"   💡 RECOMMENDATION: ✅ CREATE FOLDER")
            print(f"      Reason: {file_count} files (4+ files need folder)")
        elif file_count == 3:
            print(f"   💡 RECOMMENDATION: ⚠️  CONSIDER FOLDER")
            print(f"      Reason: {file_count} files (borderline case)")
        else:
            print(f"   💡 RECOMMENDATION: ❌ NO FOLDER NEEDED")
            print(f"      Reason: {file_count} files (keep flat structure)")
    
    print(f"\n📁 STANDALONE FILES:")
    for file in standalone_files:
        print(f"   ├── {file}")
    print(f"   💡 RECOMMENDATION: ❌ NO FOLDER NEEDED")
    print(f"      Reason: Utility files, keep in root")
    
    return tool_files, standalone_files

def generate_folder_structure_recommendation(tool_files):
    """Tạo khuyến nghị cấu trúc folder"""
    print("\n🎯 FOLDER STRUCTURE RECOMMENDATIONS:")
    print("=" * 60)
    
    print("\n✅ TOOLS THAT NEED FOLDERS:")
    for tool_name, files in tool_files.items():
        if len(files) >= 4:
            print(f"\n📁 {tool_name}/")
            print(f"   ├── __init__.py")
            for file in files:
                print(f"   ├── {file}")
    
    print("\n❌ TOOLS THAT DON'T NEED FOLDERS:")
    for tool_name, files in tool_files.items():
        if len(files) < 4:
            print(f"\n📄 {tool_name}:")
            for file in files:
                print(f"   ├── {file}")
    
    print("\n📁 CURRENT STRUCTURE (KEEP AS IS):")
    print("python/mono_tools/")
    print("├── __init__.py")
    print("├── qt.py")
    print("├── utils.py")
    print("├── test_demo/")
    print("│   ├── test_*.py")
    print("│   └── demo_*.py")
    print("└── [simple tools].py")

def generate_migration_plan(tool_files):
    """Tạo kế hoạch migration"""
    print("\n🚀 MIGRATION PLAN:")
    print("=" * 60)
    
    tools_to_migrate = [name for name, files in tool_files.items() if len(files) >= 4]
    
    if not tools_to_migrate:
        print("✅ No tools need migration - current structure is optimal!")
        return
    
    print(f"\n📋 Tools to migrate: {', '.join(tools_to_migrate)}")
    
    for tool_name in tools_to_migrate:
        print(f"\n🔧 MIGRATING {tool_name.upper()}:")
        print(f"   1. Create folder: python/mono_tools/{tool_name}/")
        print(f"   2. Create __init__.py with exports")
        print(f"   3. Move files to folder")
        print(f"   4. Update imports in __init__.py")
        print(f"   5. Test functionality")

def main():
    """Main function"""
    print("Mono Studio - Tool Structure Analyzer")
    print("Analyzing current tool organization...")
    print()
    
    try:
        tool_files, standalone_files = analyze_tool_structure()
        generate_folder_structure_recommendation(tool_files)
        generate_migration_plan(tool_files)
        
        print("\n" + "=" * 60)
        print("✅ Analysis complete!")
        print("💡 Check docs/Tool_Folder_Strategy.md for detailed guidelines")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
