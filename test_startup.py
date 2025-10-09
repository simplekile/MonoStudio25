#!/usr/bin/env python3
"""
Test script to check if startup script is working
"""

print("🧪 Test startup script loaded!")
print("🧪 This should appear in Houdini console if package is loaded")

def test_function():
    print("🧪 Test function called!")
    return True

# Test if this runs
if __name__ == "__main__":
    print("🧪 Running as main script")
    test_function()
else:
    print("🧪 Imported as module")
