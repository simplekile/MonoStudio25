#!/usr/bin/env python3
"""
Query Houdini Icons Database
Lấy danh sách icon thực tế từ database
"""

import sqlite3
import os

def query_houdini_icons():
    """Query database để lấy danh sách icon"""
    try:
        # Đường dẫn đến database
        db_path = "temp_houdini_icons/scripts/assets/icon_db.db"
        
        if not os.path.exists(db_path):
            print(f"❌ Database not found: {db_path}")
            return []
        
        # Kết nối database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query tất cả icon
        cursor.execute("SELECT name, image, category FROM icon ORDER BY name")
        icons = cursor.fetchall()
        
        print(f"Found {len(icons)} icons in database")
        print("=" * 60)
        
        # Hiển thị 20 icon đầu tiên
        print("First 20 icons:")
        for i, (name, image, category) in enumerate(icons[:20]):
            print(f"{i+1:2d}. {name:<30} | {image:<40} | {category}")
        
        print("\n" + "=" * 60)
        
        # Tìm icon phù hợp cho Mono Studio
        print("Icons suitable for Mono Studio:")
        
        # Tìm icon có chứa từ khóa liên quan
        keywords = ['folder', 'file', 'toolbar', 'material', 'texture', 'all', 'project', 'shot', 'asset']
        
        suitable_icons = []
        for name, image, category in icons:
            name_lower = name.lower()
            for keyword in keywords:
                if keyword in name_lower:
                    suitable_icons.append((name, image, category))
                    break
        
        # Hiển thị icon phù hợp
        for i, (name, image, category) in enumerate(suitable_icons[:15]):
            print(f"{i+1:2d}. {name:<30} | {image:<40} | {category}")
        
        # Tìm icon BUTTONS
        print("\nBUTTONS category icons:")
        cursor.execute("SELECT name, image, category FROM icon WHERE category = 'BUTTONS' ORDER BY name")
        button_icons = cursor.fetchall()
        
        for i, (name, image, category) in enumerate(button_icons[:15]):
            print(f"{i+1:2d}. {name:<30} | {image:<40} | {category}")
        
        conn.close()
        
        return suitable_icons
        
    except Exception as e:
        print(f"Error querying database: {e}")
        return []

def main():
    """Main function"""
    print("Querying Houdini Icons Database")
    print("=" * 50)
    
    icons = query_houdini_icons()
    
    if icons:
        print(f"\nFound {len(icons)} suitable icons")
    else:
        print("\nNo suitable icons found")

if __name__ == "__main__":
    main()
