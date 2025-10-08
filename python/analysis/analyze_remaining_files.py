"""
Analyze remaining files in root folder
"""

import os

def analyze_remaining_files():
    """Analyze files still in root folder"""
    print("Analyzing remaining files in root folder...")
    
    mono_tools_path = "python/mono_tools"
    
    # Files that should be in folders
    remaining_files = []
    
    for filename in os.listdir(mono_tools_path):
        if filename.endswith('.py') and not filename.startswith('__'):
            # Skip files that are already in folders
            if filename in ['__init__.py']:
                continue
            
            # Check if file is in a subfolder
            file_path = os.path.join(mono_tools_path, filename)
            if os.path.isfile(file_path):
                remaining_files.append(filename)
    
    print(f"Found {len(remaining_files)} files in root folder:")
    for file in remaining_files:
        print(f"  - {file}")
    
    # Categorize files
    demo_files = []
    test_files = []
    unknown_files = []
    
    for file in remaining_files:
        if file.startswith('demo_'):
            demo_files.append(file)
        elif file.startswith('test_'):
            test_files.append(file)
        else:
            unknown_files.append(file)
    
    print(f"\nCategorization:")
    print(f"  Demo files: {len(demo_files)}")
    for file in demo_files:
        print(f"    - {file}")
    
    print(f"  Test files: {len(test_files)}")
    for file in test_files:
        print(f"    - {file}")
    
    print(f"  Unknown files: {len(unknown_files)}")
    for file in unknown_files:
        print(f"    - {file}")
    
    return demo_files, test_files, unknown_files

def recommend_folder_structure(demo_files, test_files, unknown_files):
    """Recommend folder structure for remaining files"""
    print(f"\nFolder Structure Recommendations:")
    print("-" * 40)
    
    if demo_files:
        print("1. DEMO FILES - Move to test_demo/")
        for file in demo_files:
            print(f"   move {file} -> test_demo/")
    
    if test_files:
        print("2. TEST FILES - Move to test_demo/")
        for file in test_files:
            print(f"   move {file} -> test_demo/")
    
    if unknown_files:
        print("3. UNKNOWN FILES - Need analysis")
        for file in unknown_files:
            print(f"   - {file} (need to determine category)")

def main():
    """Main analysis function"""
    print("Mono Studio - Remaining Files Analysis")
    print("=" * 50)
    
    try:
        demo_files, test_files, unknown_files = analyze_remaining_files()
        recommend_folder_structure(demo_files, test_files, unknown_files)
        
        print(f"\nSummary:")
        print(f"  Total remaining files: {len(demo_files) + len(test_files) + len(unknown_files)}")
        print(f"  Demo files: {len(demo_files)}")
        print(f"  Test files: {len(test_files)}")
        print(f"  Unknown files: {len(unknown_files)}")
        
        if len(demo_files) + len(test_files) + len(unknown_files) == 0:
            print("\nSUCCESS: All files are properly organized!")
        else:
            print(f"\nACTION NEEDED: {len(demo_files) + len(test_files) + len(unknown_files)} files need to be moved to folders")
        
    except Exception as e:
        print(f"ERROR: Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
