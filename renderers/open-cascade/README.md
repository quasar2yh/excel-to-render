# Open CASCADE DXF Automated Renderer

This renderer uses **Open CASCADE Technology (OCCT)** via `pythonocc-core` to convert 2D DXF floor plans into 3D CAD geometry and automate the rendering process.

## Key Features
- **DXF Parsing**: Integrates `ezdxf` for high-fidelity DXF layer and entity handling.
- **Parametric Extrusion**: Automatically extrudes 2D lines into 3D walls, shelves, and pillars based on layer metadata.
- **Premium Visualization**: Uses OCCT's `AIS` (Application Interactive Services) for high-performance shading and gradient backgrounds.
- **Automated View Capture**: Automatically captures isometric previews as PNG.

## Prerequisites
To run this renderer, you need a Python environment with `pythonocc-core` and `ezdxf`. We recommend using **Conda**:

```powershell
# Create environment
conda create -n occt-renderer python=3.10
conda activate occt-renderer

# Install libraries
conda install -c conda-forge pythonocc-core=7.7.0 ezdxf
```

## How to Run
You can use the PowerShell wrapper or run the Python script directly:

```powershell
./render.ps1 ../../sample/floor_plan.dxf ./output.png
```

Or via `npm` (if project is initialized):
```bash
npm run render
```

## Layer Mapping
The renderer maps DXF layers to specific 3D heights and colors:
- `STRUCT_WALLS`: White, 100mm height
- `SHELVES`: Steel Blue, 60mm height
- `RETAIL_ISLANDS`: Orange, 40mm height
- `CHECKOUT`: Green, 30mm height
- `PILLARS`: Gray, 120mm height
