# 🎨 Houdini Default Icons Guide

> **Reference**: [houdini-icons.dev](https://houdini-icons.dev/) - Complete Houdini Icons Database

## 📋 **Các icon mặc định có sẵn trong Houdini**

### **🔧 MISC Icons (Miscellaneous)**
| Icon Name | Description | Usage |
|-----------|-------------|-------|
| `MISC_file` | File icon | File Manager, File operations |
| `MISC_folder` | Folder icon | Directory operations |
| `MISC_toolbar` | Toolbar icon | MiniBar, UI tools |
| `MISC_material` | Material icon | Material operations |
| `MISC_texture` | Texture icon | Texture operations |
| `MISC_all` | All/Everything icon | All tools, Global operations |
| `MISC_help` | Help icon | Help, Documentation |
| `MISC_refresh` | Refresh icon | Refresh, Reload |
| `MISC_settings` | Settings icon | Settings, Configuration |
| `MISC_info` | Info icon | Information, Details |

### **🎯 SOP Icons (Surface Operators)**
| Icon Name | Description | Usage |
|-----------|-------------|-------|
| `SOP_box` | Box icon | Geometry creation |
| `SOP_sphere` | Sphere icon | Sphere operations |
| `SOP_plane` | Plane icon | Plane operations |
| `SOP_tube` | Tube icon | Tube operations |
| `SOP_torus` | Torus icon | Torus operations |
| `SOP_grid` | Grid icon | Grid operations |
| `SOP_curve` | Curve icon | Curve operations |
| `SOP_surface` | Surface icon | Surface operations |

### **🎬 OBJ Icons (Object Operators)**
| Icon Name | Description | Usage |
|-----------|-------------|-------|
| `OBJ_camera` | Camera icon | Camera operations |
| `OBJ_light` | Light icon | Lighting operations |
| `OBJ_geometry` | Geometry icon | Geometry operations |
| `OBJ_null` | Null icon | Null objects |
| `OBJ_merge` | Merge icon | Merge operations |
| `OBJ_switch` | Switch icon | Switch operations |

### **🎨 ROP Icons (Render Operators)**
| Icon Name | Description | Usage |
|-----------|-------------|-------|
| `ROP_mantra` | Mantra icon | Mantra rendering |
| `ROP_arnold` | Arnold icon | Arnold rendering |
| `ROP_redshift` | Redshift icon | Redshift rendering |
| `ROP_vray` | V-Ray icon | V-Ray rendering |
| `ROP_octane` | Octane icon | Octane rendering |

### **⚡ DOP Icons (Dynamics Operators)**
| Icon Name | Description | Usage |
|-----------|-------------|-------|
| `DOP_gravity` | Gravity icon | Gravity operations |
| `DOP_wind` | Wind icon | Wind operations |
| `DOP_collision` | Collision icon | Collision operations |
| `DOP_fluid` | Fluid icon | Fluid operations |
| `DOP_particle` | Particle icon | Particle operations |

### **🎭 CHOP Icons (Channel Operators)**
| Icon Name | Description | Usage |
|-----------|-------------|-------|
| `CHOP_math` | Math icon | Math operations |
| `CHOP_noise` | Noise icon | Noise operations |
| `CHOP_curve` | Curve icon | Curve operations |
| `CHOP_constant` | Constant icon | Constant operations |

### **🎨 VOP Icons (VEX Operators)**
| Icon Name | Description | Usage |
|-----------|-------------|-------|
| `VOP_add` | Add icon | Add operations |
| `VOP_multiply` | Multiply icon | Multiply operations |
| `VOP_noise` | Noise icon | Noise operations |
| `VOP_color` | Color icon | Color operations |

## 🎯 **Icon Recommendations cho Mono Studio Tools**

### **File Manager**
- **Primary**: `MISC_file` - File operations
- **Alternatives**: `MISC_folder`, `MISC_all`

### **MiniBar**
- **Primary**: `MISC_toolbar` - UI toolbar
- **Alternatives**: `MISC_toolbar`, `MISC_all`

### **Material Loader**
- **Primary**: `MISC_material` - Material operations
- **Alternatives**: `MISC_material`, `MISC_all`

### **Texture Tools**
- **Primary**: `MISC_texture` - Texture operations
- **Alternatives**: `MISC_texture`, `MISC_all`

### **All Tools**
- **Primary**: `MISC_all` - All operations
- **Alternatives**: `MISC_all`, `MISC_toolbar`

## 🔧 **Cách sử dụng trong Shelf File**

```xml
<tool name="Tool_Name" label="Tool Label" icon="ICON_NAME">
  <script scriptType="python">
    <!-- Your Python code here -->
  </script>
</tool>
```

## 📝 **Lưu ý**

1. **Icon names** phải chính xác (case-sensitive)
2. **Không cần extension** (.png, .svg, etc.)
3. **Sử dụng icon có sẵn** để đảm bảo tương thích
4. **Test icon** trước khi sử dụng trong production

## 🚀 **Custom Icons**

Nếu muốn sử dụng custom icons:
1. Đặt file icon trong thư mục Houdini
2. Sử dụng đường dẫn đầy đủ: `$HOME/houdini21.0/toolbar/custom_icon.png`
3. Đảm bảo format được hỗ trợ (PNG, SVG)
