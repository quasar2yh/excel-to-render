# KeyShot DXF Rendering Automation

Automated rendering for AutoCAD DXF floor plans using **KeyShot's Python Scripting API**.

## Features

- **Layer-Based Materials**: Automatically detects 'Blueprint' layers (`STRUCT_WALLS`, `SHELVES`, etc.) and applies premium materials.
- **Premium Visualization**: Configures environment, ground reflections, and camera focus for a "WOW" effect.
- **Batch Ready**: Can be easily modified for batch processing multiple DXF files.

## Prerequisites

1.  **KeyShot** (v10 or later recommended).
2.  KeyShot executable must be in your system **PATH**, or you must update `render.ps1` with the correct path.

## How to Run

Navigate to this directory and run:

```powershell
# Using npm script wrapper
npm run render

# Directly via PowerShell with custom arguments
.\render.ps1 "..\..\sample\test_shapes.dxf" ".\custom_render.png"
```

## Material Mapping (`render_dxf.py`)

The script currently maps the following layers:

| DXF Layer | KeyShot Material (Library Name) |
| :--- | :--- |
| `STRUCT_WALLS` | `Plaster White` |
| `SHELVES` | `Blue Anodized Aluminum` |
| `RETAIL_ISLANDS` | `Orange Gloss` |
| `PILLARS` | `Brushed Aluminum` |
| `CHECKOUT` | `Green Light Emission` |

To customize these, edit the `MAT_MAPPING` dictionary in `render_dxf.py`.

## Technical Notes

- The script uses the built-in `lux` module in KeyShot.
- **Headless Mode**: KeyShot's GUI will usually open unless your license/version supports specific headless rendering flags.
- **Import Options**: Set to `snap_to_ground` and `center_geometry` for best architectural results.
