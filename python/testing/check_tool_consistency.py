"""
Script kiểm tra tính nhất quán của các tool trong Mono Studio
"""

import os
import re
from collections import defaultdict

def check_naming_conventions():
    """Kiểm tra naming conventions"""
    print("Checking Naming Conventions")
    print("=" * 40)
    
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
                if not filename.startswith('file_manager'):
                    issues.append(f"❌ {filename}: Should start with 'file_manager' not 'fm_'")
            
            elif filename.startswith('texture_'):
                if not filename in ['texture_search_replace.py', 'texture_menu_integration.py']:
                    issues.append(f"❌ {filename}: Inconsistent texture naming")
            
            elif filename.startswith('material_'):
                if not filename in ['material_loader.py']:
                    issues.append(f"❌ {filename}: Inconsistent material naming")
            
            elif filename in ['qt.py', 'utils.py']:
                continue  # These are fine
            
            else:
                # Check if it follows [tool_name].py pattern
                if '_' in filename and not filename.endswith('_menu_integration.py'):
                    tool_name = filename.replace('.py', '')
                    if not re.match(r'^[a-z]+(_[a-z]+)*$', tool_name):
                        issues.append(f"❌ {filename}: Should follow snake_case pattern")
    
    if issues:
        for issue in issues:
            print(issue)
    else:
        print("✅ All files follow naming conventions")
    
    return len(issues) == 0

def check_function_naming():
    """Kiểm tra function naming trong files"""
    print("\nChecking Function Naming")
    print("=" * 40)
    
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
                        issues.append(f"❌ {filename}: Function '{func}' should follow show_[tool_name] pattern")
                
                # Check for setup_ functions
                setup_functions = re.findall(r'def (setup_\w+)\(', content)
                for func in setup_functions:
                    if not re.match(r'^setup_[a-z]+(_[a-z]+)*$', func):
                        issues.append(f"❌ {filename}: Function '{func}' should follow setup_[tool_name] pattern")
                
            except Exception as e:
                issues.append(f"❌ {filename}: Error reading file - {e}")
    
    if issues:
        for issue in issues:
            print(issue)
    else:
        print("✅ All functions follow naming conventions")
    
    return len(issues) == 0

def check_menu_integration():
    """Kiểm tra menu integration"""
    print("\nChecking Menu Integration")
    print("=" * 40)
    
    mono_tools_path = "python/mono_tools"
    tools_with_menu = []
    tools_without_menu = []
    
    # Check for main tool files
    main_tools = []
    for filename in os.listdir(mono_tools_path):
        if filename.endswith('.py') and not filename.startswith('__'):
            if filename in ['qt.py', 'utils.py']:
                continue
            if not filename.endswith('_menu_integration.py') and not filename.startswith('fm_'):
                main_tools.append(filename.replace('.py', ''))
    
    # Check for menu integration files
    for tool in main_tools:
        menu_file = f"{tool}_menu_integration.py"
        if os.path.exists(os.path.join(mono_tools_path, menu_file)):
            tools_with_menu.append(tool)
        else:
            tools_without_menu.append(tool)
    
    if tools_with_menu:
        print("✅ Tools with menu integration:")
        for tool in tools_with_menu:
            print(f"   - {tool}")
    
    if tools_without_menu:
        print("❌ Tools without menu integration:")
        for tool in tools_without_menu:
            print(f"   - {tool}")
    
    return len(tools_without_menu) == 0

def check_package_exports():
    """Kiểm tra package exports"""
    print("\nChecking Package Exports")
    print("=" * 40)
    
    init_file = "python/mono_tools/__init__.py"
    
    try:
        with open(init_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for show_ functions in exports
        show_exports = re.findall(r"show_\w+", content)
        if show_exports:
            print("✅ Show functions in exports:")
            for export in show_exports:
                print(f"   - {export}")
        else:
            print("❌ No show functions found in exports")
        
        # Check for setup_ functions in exports
        setup_exports = re.findall(r"setup_\w+", content)
        if setup_exports:
            print("✅ Setup functions in exports:")
            for export in setup_exports:
                print(f"   - {export}")
        else:
            print("❌ No setup functions found in exports")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading {init_file}: {e}")
        return False

def check_documentation():
    """Kiểm tra documentation"""
    print("\nChecking Documentation")
    print("=" * 40)
    
    docs_path = "docs"
    if not os.path.exists(docs_path):
        print("❌ No docs folder found")
        return False
    
    doc_files = [f for f in os.listdir(docs_path) if f.endswith('.md')]
    
    if doc_files:
        print("✅ Documentation files found:")
        for doc in doc_files:
            print(f"   - {doc}")
    else:
        print("❌ No documentation files found")
    
    return len(doc_files) > 0

def generate_consistency_report():
    """Tạo báo cáo tính nhất quán"""
    print("Mono Studio - Tool Consistency Report")
    print("=" * 50)
    
    checks = [
        ("Naming Conventions", check_naming_conventions),
        ("Function Naming", check_function_naming),
        ("Menu Integration", check_menu_integration),
        ("Package Exports", check_package_exports),
        ("Documentation", check_documentation)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ Error in {check_name}: {e}")
            results[check_name] = False
    
    print("\n" + "=" * 50)
    print("CONSISTENCY SUMMARY:")
    print("=" * 50)
    
    passed = 0
    total = len(checks)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All tools are consistent!")
    else:
        print("⚠️ Some tools need standardization")
        print("💡 Check docs/Tool_Consistency_Rules.md for guidelines")
    
    return passed == total

if __name__ == "__main__":
    generate_consistency_report()
