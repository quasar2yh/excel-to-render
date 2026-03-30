# Blender DXF Renderer

This module provides automated rendering for AutoCAD DXF floor plans using Blender.

## Prerequisites

- [Blender](https://www.blender.org/download/) (Version 3.6 or higher recommended).
- Ensure `blender` is in your system PATH or installed in the default `C:\Program Files\Blender Foundation\` directory.

## Features

- **Automated Import**: Automatically enables the `io_import_dxf` addon and imports the specified DXF file.
- **3D Depth**: Automatically adds thickness (Solidify) and height to 2D lines based on their DXF layer names (e.g., `STRUCT_WALLS`, `SHELVES`).
- **Premium Materials**: Uses a curated dark-themed architectural style with reflective floors and glowing highlights.
- **Cinematic Lighting**: Configured with Area lights and Eevee Bloom/SSR for a premium look.

## Usage

### Using NPM
From the `renderers/blender` directory:
```bash
npm run render
```

### Using PowerShell
```powershell
./render.ps1 ../../sample/floor_plan.dxf ./output.png
```

## Structure

- `render_dxf.py`: The core Blender Python script that performs the scene setup and rendering.
- `render.ps1`: A helper script for Windows that locates Blender and handles path resolution.
- `package.json`: NPM scripts for easy execution.
