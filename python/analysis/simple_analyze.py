"""
Simple tool structure analyzer
"""

import os
from collections import defaultdict

def analyze_tools():
    """Analyze current tool structure"""
    print("Mono Studio Tool Structure Analysis")
    print("=" * 50)
    
    mono_tools_path = "python/mono_tools"
    tool_files = defaultdict(list)
    standalone_files = []
    
    for filename in os.listdir(mono_tools_path):
        if filename.endswith('.py') and not filename.startswith('__'):
            # Skip test files
            if filename in ['test_pyside6.py', 'verify_pyside6.py', 'test_texture_search_replace.py', 
                           'demo_texture_search_replace.py', 'quick_test_pyside6.py']:
                continue
                
            # Categorize by pattern
            if filename.startswith('fm_'):
                tool_files['file_manager'].append(filename)
            elif filename.startswith('texture_'):
                tool_files['texture_search_replace'].append(filename)
            elif filename.startswith('material_'):
                tool_files['material_loader'].append(filename)
            elif filename in ['qt.py', 'utils.py']:
                standalone_files.append(filename)
            else:
                tool_name = filename.replace('.py', '').replace('_menu_integration', '')
                tool_files[tool_name].append(filename)
    
    # Show results
    print("\nTool Analysis:")
    print("-" * 30)
    
    for tool_name, files in tool_files.items():
        file_count = len(files)
        print(f"\n{tool_name.upper()}: {file_count} files")
        for file in files:
            print(f"  - {file}")
        
        if file_count >= 4:
            print(f"  -> RECOMMENDATION: CREATE FOLDER")
        elif file_count == 3:
            print(f"  -> RECOMMENDATION: CONSIDER FOLDER")
        else:
            print(f"  -> RECOMMENDATION: NO FOLDER NEEDED")
    
    print(f"\nStandalone files:")
    for file in standalone_files:
        print(f"  - {file}")
    print(f"  -> RECOMMENDATION: NO FOLDER NEEDED")
    
    return tool_files, standalone_files

def show_recommendations(tool_files):
    """Show folder recommendations"""
    print("\nFOLDER RECOMMENDATIONS:")
    print("=" * 30)
    
    tools_needing_folders = [name for name, files in tool_files.items() if len(files) >= 4]
    
    if tools_needing_folders:
        print("Tools that NEED folders:")
        for tool in tools_needing_folders:
            print(f"  - {tool}/ (has {len(tool_files[tool])} files)")
    else:
        print("No tools need folders - current structure is optimal!")
    
    print("\nTools that DON'T need folders:")
    for tool_name, files in tool_files.items():
        if len(files) < 4:
            print(f"  - {tool_name} ({len(files)} files)")

if __name__ == "__main__":
    tool_files, standalone_files = analyze_tools()
    show_recommendations(tool_files)
