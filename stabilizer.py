# Emergency MiniBar Stabilizer - Fix Erratic Jumping
# Run trong Houdini Python console:
# exec(open(r"d:\Dropbox\Stock\Plugin\HOU\MonoStudio\stabilizer.py").read())

try:
    import sys, os
    
    # Add path nếu cần
    plugin_path = r"d:\Dropbox\Stock\Plugin\HOU\MonoStudio\python"
    if plugin_path not in sys.path:
        sys.path.append(plugin_path)
    
    import hou
    from mono_tools.qt import QtCore
    
    print("🛡️ EMERGENCY MINIBAR STABILIZER 🛡️")
    
    # Find all MiniBars
    minibars = []
    for widget in hou.qt.mainWindow().findChildren(QtCore.QObject, "MonoMiniBar"):
        if hasattr(widget, 'pos') and widget.isVisible():
            minibars.append(widget)
    
    if minibars:
        print(f"📍 Found {len(minibars)} MiniBar(s)")
        
        for i, minibar in enumerate(minibars):
            print(f"\n🔧 Stabilizing MiniBar #{i+1}:")
            
            # Show current erratic position
            pos = minibar.pos()
            mw = hou.qt.mainWindow()
            
            if mw:
                geo = mw.geometry()
                rel_x = (pos.x() + minibar.width() - geo.x()) / geo.width()
                rel_y = (pos.y() - geo.y()) / geo.height()
                
                print(f"   • Current erratic: pos({pos.x()}, {pos.y()}) = rel({rel_x:.3f}, {rel_y:.3f})")
                
                # COMPLETE SHUTDOWN of automatic positioning
                print("   🛑 DISABLING ALL AUTOMATIC POSITIONING...")
                
                # Stop and remove main window event timer
                if hasattr(minibar, '_main_window_change_timer') and minibar._main_window_change_timer:
                    minibar._main_window_change_timer.stop()
                    minibar._main_window_change_timer.deleteLater()
                    minibar._main_window_change_timer = None
                    print("   ❌ Main window change timer destroyed")
                
                # Remove event filter completely
                if hasattr(minibar, '_main_window_filter'):
                    try:
                        mw.removeEventFilter(minibar._main_window_filter)
                        minibar._main_window_filter = None
                        print("   ❌ Event filter completely removed")
                    except:
                        pass
                
                # Set multiple lock flags
                minibar._updating_position = True
                minibar._position_locked = True
                minibar._auto_positioning_disabled = True
                print("   🔒 Multiple position locks activated")
                
                # Completely disable the problematic methods
                def _disabled_update(self):
                    """Completely disabled to prevent jumping"""
                    pass
                
                def _disabled_save(self):
                    """Disabled save to prevent feedback loops"""
                    pass
                
                # Override methods with disabled versions
                minibar._update_position_relative_to_main_window = lambda: _disabled_update(minibar)
                minibar._save_relative_position = lambda: _disabled_save(minibar)
                print("   🚫 Position methods completely disabled")
                
                # Reset to stable position
                print("   🎯 Forcing stable position...")
                
                # Calculate correct position manually (no auto-save)
                target_rel_x, target_rel_y = 0.915, 0.000
                target_x = geo.x() + int(target_rel_x * geo.width()) - minibar.width()
                target_y = geo.y() + int(target_rel_y * geo.height())
                
                # Direct move without triggering any save/update logic
                minibar.move(target_x, target_y)
                
                # Verify final position
                final_pos = minibar.pos()
                final_rel_x = (final_pos.x() + minibar.width() - geo.x()) / geo.width()
                final_rel_y = (final_pos.y() - geo.y()) / geo.height()
                
                print(f"   ✅ STABILIZED: pos({final_pos.x()}, {final_pos.y()}) = rel({final_rel_x:.3f}, {final_rel_y:.3f})")
                
                # Add visual indicator that it's stabilized
                if hasattr(minibar, 'handle_area'):
                    minibar.handle_area.setText("📌")  # Pin icon to show it's locked
                    minibar.handle_area.setToolTip("Position stabilized - no automatic updates")
        
        print(f"\n✅ STABILIZATION COMPLETE")
        print(f"📌 MiniBar is now LOCKED at stable position")
        print(f"🚫 ALL automatic positioning DISABLED")
        print(f"🛡️ No more erratic jumping or position drift")
        print(f"📍 MiniBar will stay exactly where placed")
        
        print(f"\n💡 Status:")
        print(f"   • Event filter: REMOVED")
        print(f"   • Auto-updates: DISABLED") 
        print(f"   • Position: LOCKED at (0.915, 0.000)")
        print(f"   • Manual drag: Still works")
        
        print(f"\n🔄 To restore normal behavior:")
        print(f"   • Restart Houdini")
        print(f"   • The enhanced code will be more stable")
        
    else:
        print("❌ No MiniBar found")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()