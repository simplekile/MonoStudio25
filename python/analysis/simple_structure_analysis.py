"""
Simple structure analysis without unicode characters
"""

import os
from collections import defaultdict

def analyze_structure():
    """Analyze current folder structure"""
    print("Mono Studio - Current Structure Analysis")
    print("=" * 50)
    
    mono_tools_path = "python/mono_tools"
    
    # Categorize files by tool
    tool_files = defaultdict(list)
    standalone_files = []
    test_files = []
    
    for filename in os.listdir(mono_tools_path):
        if filename.endswith('.py') and not filename.startswith('__'):
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
    
    return tool_files, standalone_files, test_files

def categorize_tools(tool_files):
    """Categorize tools by complexity"""
    print("\nTool Classification:")
    print("-" * 30)
    
    simple_tools = []
    medium_tools = []
    complex_tools = []
    
    for tool_name, files in tool_files.items():
        file_count = len(files)
        
        if file_count <= 2:
            simple_tools.append((tool_name, files, file_count))
        elif file_count <= 4:
            medium_tools.append((tool_name, files, file_count))
        else:
            complex_tools.append((tool_name, files, file_count))
    
    # Display results
    if complex_tools:
        print("\nCOMPLEX TOOLS (5+ files - NEED FOLDERS):")
        for tool_name, files, count in complex_tools:
            print(f"  {tool_name}: {count} files")
            for file in files:
                print(f"    - {file}")
    
    if medium_tools:
        print("\nMEDIUM TOOLS (3-4 files - CONSIDER FOLDERS):")
        for tool_name, files, count in medium_tools:
            print(f"  {tool_name}: {count} files")
            for file in files:
                print(f"    - {file}")
    
    if simple_tools:
        print("\nSIMPLE TOOLS (1-2 files - FOR CONSISTENCY):")
        for tool_name, files, count in simple_tools:
            print(f"  {tool_name}: {count} files")
            for file in files:
                print(f"    - {file}")
    
    return simple_tools, medium_tools, complex_tools

def analyze_file_relationships(tool_files):
    """Analyze file relationships"""
    print("\nFile Relationship Analysis:")
    print("-" * 30)
    
    for tool_name, files in tool_files.items():
        print(f"\n{tool_name.upper()}:")
        
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
                helper_files.append(file)
            else:
                main_files.append(file)
        
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

def check_naming_issues(tool_files):
    """Check naming consistency"""
    print("\nNaming Consistency Check:")
    print("-" * 30)
    
    issues = []
    
    for tool_name, files in tool_files.items():
        for file in files:
            if file.startswith('fm_'):
                issues.append(f"ISSUE: {file} should start with 'file_manager' not 'fm_'")
    
    if issues:
        print("Naming Issues Found:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("OK: All files follow naming conventions")
    
    return len(issues) == 0

def recommend_folder_structure(simple_tools, medium_tools, complex_tools, standalone_files):
    """Recommend folder structure"""
    print("\nFolder Structure Recommendations:")
    print("-" * 40)
    
    print("\n1. COMPLEX TOOLS (Must have folders):")
    for tool_name, files, count in complex_tools:
        print(f"  {tool_name}/ ({count} files)")
        print(f"    + __init__.py")
        for file in files:
            print(f"    + {file}")
    
    print("\n2. MEDIUM TOOLS (Should have folders for consistency):")
    for tool_name, files, count in medium_tools:
        print(f"  {tool_name}/ ({count} files)")
        print(f"    + __init__.py")
        for file in files:
            print(f"    + {file}")
    
    print("\n3. SIMPLE TOOLS (Should have folders for consistency):")
    for tool_name, files, count in simple_tools:
        print(f"  {tool_name}/ ({count} files)")
        print(f"    + __init__.py")
        for file in files:
            print(f"    + {file}")
    
    print("\n4. STANDALONE FILES (Should have folders for consistency):")
    for file in standalone_files:
        tool_name = file.replace('.py', '')
        print(f"  {tool_name}/")
        print(f"    + __init__.py")
        print(f"    + {file}")

def generate_migration_commands(simple_tools, medium_tools, complex_tools, standalone_files):
    """Generate migration commands"""
    print("\nMigration Commands:")
    print("-" * 30)
    
    print("\n# Phase 1: Create folders")
    all_tools = []
    
    for tool_name, files, count in complex_tools:
        all_tools.append(tool_name)
    for tool_name, files, count in medium_tools:
        all_tools.append(tool_name)
    for tool_name, files, count in simple_tools:
        all_tools.append(tool_name)
    
    for file in standalone_files:
        tool_name = file.replace('.py', '')
        all_tools.append(tool_name)
    
    for tool in all_tools:
        print(f"mkdir python/mono_tools/{tool}")
    
    print("\n# Phase 2: Move files")
    for tool_name, files, count in complex_tools:
        for file in files:
            print(f"move python/mono_tools/{file} python/mono_tools/{tool_name}/")
    
    for tool_name, files, count in medium_tools:
        for file in files:
            print(f"move python/mono_tools/{file} python/mono_tools/{tool_name}/")
    
    for tool_name, files, count in simple_tools:
        for file in files:
            print(f"move python/mono_tools/{file} python/mono_tools/{tool_name}/")
    
    for file in standalone_files:
        tool_name = file.replace('.py', '')
        print(f"move python/mono_tools/{file} python/mono_tools/{tool_name}/")
    
    print("\n# Phase 3: Create __init__.py files")
    print("# Create __init__.py for each tool folder with proper exports")
    
    print("\n# Phase 4: Update main __init__.py")
    print("# Update imports to use new folder structure")

def main():
    """Main analysis function"""
    try:
        # Analyze structure
        tool_files, standalone_files, test_files = analyze_structure()
        
        # Categorize tools
        simple_tools, medium_tools, complex_tools = categorize_tools(tool_files)
        
        # Analyze relationships
        analyze_file_relationships(tool_files)
        
        # Check naming
        naming_ok = check_naming_issues(tool_files)
        
        # Recommend structure
        recommend_folder_structure(simple_tools, medium_tools, complex_tools, standalone_files)
        
        # Generate commands
        generate_migration_commands(simple_tools, medium_tools, complex_tools, standalone_files)
        
        print("\n" + "=" * 50)
        print("Analysis Summary:")
        print(f"- Complex tools: {len(complex_tools)}")
        print(f"- Medium tools: {len(medium_tools)}")
        print(f"- Simple tools: {len(simple_tools)}")
        print(f"- Standalone files: {len(standalone_files)}")
        print(f"- Naming consistent: {naming_ok}")
        
        print("\nRecommendation: Create folders for ALL tools for consistency")
        
    except Exception as e:
        print(f"ERROR: Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
