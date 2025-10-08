"""
Test syntax only - no actual imports
"""

import ast
import os

def test_syntax():
    """Test Python syntax without importing"""
    print("Testing Python syntax...")
    
    mono_tools_path = "python/mono_tools"
    
    # Files to test
    files_to_test = [
        "file_manager/file_manager_api.py",
        "file_manager/file_manager_manager.py", 
        "file_manager/file_manager_minibar.py",
        "file_manager/file_manager_helpers.py",
        "file_manager/file_manager_models.py",
        "file_manager/file_manager_menu_integration.py",
        "texture_search_replace/texture_search_replace.py",
        "texture_search_replace/texture_menu_integration.py",
        "material_loader/material_loader.py",
        "material_loader/material_loader_menu_integration.py",
        "qt/qt.py",
        "utils/utils.py"
    ]
    
    errors = []
    
    for file_path in files_to_test:
        full_path = os.path.join(mono_tools_path, file_path)
        
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse syntax
                ast.parse(content)
                print(f"OK: {file_path}")
                
            except SyntaxError as e:
                error_msg = f"SYNTAX ERROR in {file_path}: {e}"
                print(error_msg)
                errors.append(error_msg)
                
            except Exception as e:
                error_msg = f"ERROR in {file_path}: {e}"
                print(error_msg)
                errors.append(error_msg)
        else:
            error_msg = f"FILE NOT FOUND: {file_path}"
            print(error_msg)
            errors.append(error_msg)
    
    if errors:
        print(f"\nFound {len(errors)} errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("\nSUCCESS: All files have valid Python syntax!")
        return True

def main():
    """Main test function"""
    print("Mono Studio - Syntax Test")
    print("=" * 30)
    
    success = test_syntax()
    
    if success:
        print("\nAll files have valid syntax!")
        print("The import issues are likely due to missing Houdini environment.")
    else:
        print("\nSome files have syntax errors.")
        print("Check the errors above for details.")
    
    return success

if __name__ == "__main__":
    main()
