"""
Replace print statements with debug_print in minibar
"""
import re

# Read file
with open('python/mono_tools/file_manager/file_manager_minibar.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace patterns
# Match print( but not debug_print( or if.*print(
replacements = [
    (r'(\s+)print\(', r'\1debug_print('),  # Indented print
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# Keep error prints (already have if DEBUG check)
content = content.replace('if os.environ.get(\'MONO_DEBUG\'):\n                debug_print(', 
                          'if DEBUG:\n                debug_print(')

# Write back
with open('python/mono_tools/file_manager/file_manager_minibar.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Replaced all print() with debug_print()")
print("To enable debug mode: Set environment variable MONO_DEBUG=1")

