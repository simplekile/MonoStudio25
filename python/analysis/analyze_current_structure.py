"""
Script phân tích cấu trúc folder hiện tại và phân loại files
"""

import os
from collections import defaultdict
from pathlib import Path

def analyze_file_structure():
    """Phân tích cấu trúc file hiện tại"""
    print("Mono Studio - Current Structure Analysis")
    print("=" * 50)
    
    mono_tools_path = Path("python/mono_tools")
    
    # Phân loại files theo tool
    tool_files = defaultdict(list)
    standalone_files = []
    test_files = []
    
    for item in mono_tools_path.iterdir():
        if item.is_file() and item.suffix == '.py':
            filename = item.name
            
            # Skip __init__.py
            if filename == '__init__.py':
                continue
            
            # Phân loại theo pattern
            if filename.startswith('fm_'):
                tool_files['file_manager'].append(filename)
            elif filename.startswith('texture_'):
                tool_files['texture_search_replace'].append(filename)
            elif filename.startswith('material_'):
                tool_files['material_loader'].append(filename)
            elif filename.startswith('file_manager'):
                tool_files['file_manager'].append(filename)
            elif filename in ['qt.py', 'utils.py']:
                standalone_files.append(filename)
            elif filename.startswith(('test_', 'demo_', 'verify_', 'quick_test_')):
                test_files.append(filename)
            else:
                # Unknown files
                tool_files['unknown'].append(filename)
    
    return tool_files, standalone_files, test_files

def categorize_tools(tool_files):
    """Phân loại tools theo độ phức tạp"""
    print("\nTool Classification:")
    print("-" * 30)
    
    categories = {
        'simple': [],      # 1-2 files
        'medium': [],      # 3-4 files  
        'complex': []      # 5+ files
    }
    
    for tool_name, files in tool_files.items():
        if tool_name == 'unknown':
            continue
            
        file_count = len(files)
        
        if file_count <= 2:
            categories['simple'].append((tool_name, files, file_count))
        elif file_count <= 4:
            categories['medium'].append((tool_name, files, file_count))
        else:
            categories['complex'].append((tool_name, files, file_count))
    
    # Hiển thị kết quả phân loại
    for category, tools in categories.items():
        if tools:
            print(f"\n{category.upper()} TOOLS ({len(tools)} tools):")
            for tool_name, files, count in tools:
                print(f"  {tool_name}: {count} files")
                for file in files:
                    print(f"    - {file}")
    
    return categories

def analyze_file_relationships(tool_files):
    """Phân tích mối quan hệ giữa các files"""
    print("\nFile Relationship Analysis:")
    print("-" * 30)
    
    for tool_name, files in tool_files.items():
        if tool_name == 'unknown':
            continue
            
        print(f"\n{tool_name.upper()}:")
        
        # Phân loại files theo chức năng
        main_files = []
        integration_files = []
        helper_files = []
        model_files = []
        api_files = []
        
        for file in files:
            if file.endswith('_menu_integration.py'):
                integration_files.append(file)
            elif file.endswith('_helpers.py') or file.startswith('fm_helpers'):
                helper_files.append(file)
            elif file.endswith('_models.py') or file.startswith('fm_models'):
                model_files.append(file)
            elif file.endswith('_api.py') or file.startswith('file_manager_api'):
                api_files.append(file)
            elif file.startswith('fm_'):
                # File manager sub-components
                if 'manager' in file:
                    helper_files.append(file)
                elif 'minibar' in file:
                    helper_files.append(file)
                else:
                    helper_files.append(file)
            else:
                main_files.append(file)
        
        # Hiển thị phân loại
        if main_files:
            print(f"  Main files: {', '.join(main_files)}")
        if integration_files:
            print(f"  Integration: {', '.join(integration_files)}")
        if helper_files:
            print(f"  Helpers: {', '.join(helper_files)}")
        if model_files:
            print(f"  Models: {', '.join(model_files)}")
        if api_files:
            print(f"  API: {', '.join(api_files)}")

def recommend_folder_structure(categories):
    """Đưa ra khuyến nghị cấu trúc folder"""
    print("\nFolder Structure Recommendations:")
    print("-" * 40)
    
    print("\n1. COMPLEX TOOLS (Need folders):")
    for tool_name, files, count in categories['complex']:
        print(f"  {tool_name}/ ({count} files)")
        print(f"    ├── __init__.py")
        for file in files:
            print(f"    ├── {file}")
        print(f"    └── [test files in test_demo/]")
    
    print("\n2. MEDIUM TOOLS (Consider folders):")
    for tool_name, files, count in categories['medium']:
        print(f"  {tool_name}/ ({count} files) - OPTIONAL")
        print(f"    ├── __init__.py")
        for file in files:
            print(f"    ├── {file}")
        print(f"    └── [test files in test_demo/]")
    
    print("\n3. SIMPLE TOOLS (Keep flat or create folders):")
    for tool_name, files, count in categories['simple']:
        print(f"  {tool_name}/ ({count} files) - FOR CONSISTENCY")
        print(f"    ├── __init__.py")
        for file in files:
            print(f"    ├── {file}")
        print(f"    └── [test files in test_demo/]")
    
    print("\n4. STANDALONE FILES:")
    print("  qt/")
    print("    ├── __init__.py")
    print("    └── qt.py")
    print("  utils/")
    print("    ├── __init__.py")
    print("    └── utils.py")

def check_naming_consistency(tool_files):
    """Kiểm tra tính nhất quán trong naming"""
    print("\nNaming Consistency Check:")
    print("-" * 30)
    
    issues = []
    
    for tool_name, files in tool_files.items():
        if tool_name == 'unknown':
            continue
            
        # Check file naming patterns
        for file in files:
            if file.startswith('fm_'):
                issues.append(f"ISSUE: {file} should start with 'file_manager' not 'fm_'")
            elif file.startswith('texture_') and not file in ['texture_search_replace.py', 'texture_menu_integration.py']:
                issues.append(f"ISSUE: {file} inconsistent texture naming")
            elif file.startswith('material_') and not file in ['material_loader.py']:
                issues.append(f"ISSUE: {file} inconsistent material naming")
    
    if issues:
        print("Naming Issues Found:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ All files follow naming conventions")

def generate_migration_plan(categories):
    """Tạo kế hoạch migration cụ thể"""
    print("\nDetailed Migration Plan:")
    print("-" * 30)
    
    print("\nPhase 1: Create folders for all tools")
    print("Commands:")
    
    all_tools = []
    for category_tools in categories.values():
        for tool_name, files, count in category_tools:
            all_tools.append(tool_name)
    
    # Add standalone tools
    all_tools.extend(['qt', 'utils'])
    
    for tool in all_tools:
        print(f"  mkdir python/mono_tools/{tool}")
    
    print("\nPhase 2: Move files to folders")
    print("Commands:")
    
    for tool_name, files, count in categories['complex']:
        for file in files:
            print(f"  move python/mono_tools/{file} python/mono_tools/{tool_name}/")
    
    for tool_name, files, count in categories['medium']:
        for file in files:
            print(f"  move python/mono_tools/{file} python/mono_tools/{tool_name}/")
    
    for tool_name, files, count in categories['simple']:
        for file in files:
            print(f"  move python/mono_tools/{file} python/mono_tools/{tool_name}/")
    
    print("  move python/mono_tools/qt.py python/mono_tools/qt/")
    print("  move python/mono_tools/utils.py python/mono_tools/utils/")
    
    print("\nPhase 3: Create __init__.py files")
    print("  Create __init__.py for each tool folder with proper exports")
    
    print("\nPhase 4: Update main __init__.py")
    print("  Update imports to use new folder structure")

def main():
    """Main analysis function"""
    try:
        # Analyze current structure
        tool_files, standalone_files, test_files = analyze_file_structure()
        
        # Categorize tools
        categories = categorize_tools(tool_files)
        
        # Analyze relationships
        analyze_file_relationships(tool_files)
        
        # Check naming consistency
        check_naming_consistency(tool_files)
        
        # Recommend structure
        recommend_folder_structure(categories)
        
        # Generate migration plan
        generate_migration_plan(categories)
        
        print("\n" + "=" * 50)
        print("Analysis Complete!")
        print("Check the recommendations above for migration planning.")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
