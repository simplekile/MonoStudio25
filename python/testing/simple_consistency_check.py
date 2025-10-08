"""
Simple tool consistency checker
"""

import os
import re

def check_naming():
    """Check file naming conventions"""
    print("Checking File Naming")
    print("-" * 30)
    
    mono_tools_path = "python/mono_tools"
    issues = []
    
    for filename in os.listdir(mono_tools_path):
        if filename.endswith('.py') and not filename.startswith('__'):
            # Skip test files
            if filename in ['test_pyside6.py', 'verify_pyside6.py', 'test_texture_search_replace.py', 
                           'demo_texture_search_replace.py', 'quick_test_pyside6.py']:
                continue
            
            # Check naming patterns
            if filename.startswith('fm_'):
                issues.append(f"ISSUE: {filename} should start with 'file_manager' not 'fm_'")
            elif filename.startswith('texture_'):
                if not filename in ['texture_search_replace.py', 'texture_menu_integration.py']:
                    issues.append(f"ISSUE: {filename} inconsistent texture naming")
            elif filename.startswith('material_'):
                if not filename in ['material_loader.py']:
                    issues.append(f"ISSUE: {filename} inconsistent material naming")
    
    if issues:
        for issue in issues:
            print(issue)
        return False
    else:
        print("OK: All files follow naming conventions")
        return True

def check_functions():
    """Check function naming"""
    print("\nChecking Function Naming")
    print("-" * 30)
    
    mono_tools_path = "python/mono_tools"
    issues = []
    
    for filename in os.listdir(mono_tools_path):
        if filename.endswith('.py') and not filename.startswith('__'):
            filepath = os.path.join(mono_tools_path, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for show_ functions
                show_functions = re.findall(r'def (show_\w+)\(', content)
                for func in show_functions:
                    if not re.match(r'^show_[a-z]+(_[a-z]+)*$', func):
                        issues.append(f"ISSUE: {filename} function '{func}' should follow show_[tool_name] pattern")
                
            except Exception as e:
                issues.append(f"ISSUE: {filename} error reading file - {e}")
    
    if issues:
        for issue in issues:
            print(issue)
        return False
    else:
        print("OK: All functions follow naming conventions")
        return True

def check_menu_integration():
    """Check menu integration"""
    print("\nChecking Menu Integration")
    print("-" * 30)
    
    mono_tools_path = "python/mono_tools"
    
    # Main tools
    main_tools = []
    for filename in os.listdir(mono_tools_path):
        if filename.endswith('.py') and not filename.startswith('__'):
            if filename in ['qt.py', 'utils.py']:
                continue
            if not filename.endswith('_menu_integration.py') and not filename.startswith('fm_'):
                main_tools.append(filename.replace('.py', ''))
    
    # Check for menu integration
    tools_with_menu = []
    tools_without_menu = []
    
    for tool in main_tools:
        menu_file = f"{tool}_menu_integration.py"
        if os.path.exists(os.path.join(mono_tools_path, menu_file)):
            tools_with_menu.append(tool)
        else:
            tools_without_menu.append(tool)
    
    if tools_with_menu:
        print("OK: Tools with menu integration:")
        for tool in tools_with_menu:
            print(f"  - {tool}")
    
    if tools_without_menu:
        print("ISSUE: Tools without menu integration:")
        for tool in tools_without_menu:
            print(f"  - {tool}")
        return False
    
    return True

def check_package_exports():
    """Check package exports"""
    print("\nChecking Package Exports")
    print("-" * 30)
    
    init_file = "python/mono_tools/__init__.py"
    
    try:
        with open(init_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for show_ functions
        show_exports = re.findall(r"show_\w+", content)
        if show_exports:
            print("OK: Show functions in exports:")
            for export in show_exports:
                print(f"  - {export}")
        else:
            print("ISSUE: No show functions found in exports")
            return False
        
        return True
        
    except Exception as e:
        print(f"ISSUE: Error reading {init_file}: {e}")
        return False

def main():
    """Main consistency check"""
    print("Mono Studio - Tool Consistency Check")
    print("=" * 50)
    
    checks = [
        ("File Naming", check_naming),
        ("Function Naming", check_functions),
        ("Menu Integration", check_menu_integration),
        ("Package Exports", check_package_exports)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"ERROR in {check_name}: {e}")
            results[check_name] = False
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print("=" * 50)
    
    passed = 0
    total = len(checks)
    
    for check_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{check_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("All tools are consistent!")
    else:
        print("Some tools need standardization")
        print("Check docs/Tool_Consistency_Rules.md for guidelines")

if __name__ == "__main__":
    main()
