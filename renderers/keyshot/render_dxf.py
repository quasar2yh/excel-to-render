import lux
import os
import sys

# Keyshot DXF Automation Script
# Designed for 'Blueprint' project DXF layers

# Material Mapping (KeyShot Library Names)
# Note: These names should match your KeyShot Library or be imported into the scene
MAT_MAPPING = {
    "STRUCT_WALLS": "Plaster White",
    "SHELVES": "Blue Anodized Aluminum",
    "RETAIL_ISLANDS": "Orange Gloss",
    "PILLARS": "Brushed Aluminum",
    "CHECKOUT": "Green Light Emission"
}

def setup_environment():
    """Sets a premium studio environment."""
    # KeyShot usually has built-in environments. 
    # 'Interior' environments work well for architectural floor plans.
    try:
        lux.setEnvironment("Interior_Studio.hdz")
    except:
        # Fallback if specific file is not found
        lux.setBackgroundColor((0.05, 0.05, 0.08))

def center_camera():
    """Focuses the camera on the imported geometry."""
    # center top-down view or isometric
    lux.setCameraLookAt(0, 0, 0) # Fallback to origin
    # Better: use lux.getSceneTree().getBounds() if available in your version
    pass

def apply_materials():
    """Applies materials based on DXF layer names found in the scene tree."""
    root = lux.getSceneTree()
    
    # Iterate through each mapping
    for layer_name, mat_name in MAT_MAPPING.items():
        # Find nodes containing the layer name (Case insensitive check)
        # Note: root.find() returns a list of SceneNode objects
        nodes = root.find(name=layer_name)
        
        if nodes:
            print(f"[KeyShot] Found {len(nodes)} nodes for layer {layer_name}")
            for node in nodes:
                try:
                    lux.setMaterial(node, mat_name)
                    print(f"  Applied {mat_name} to {node.getName()}")
                except Exception as e:
                    print(f"  Failed to apply material to {node.getName()}: {e}")

def main():
    # KeyShot script arguments are often passed via sys.argv if run from CLI
    # Default paths if not provided
    dxf_path = os.path.abspath("../../sample/floor_plan.dxf")
    output_path = os.path.abspath("./keyshot_render.png")

    # If launched from CLI with arguments
    if len(sys.argv) > 1:
        dxf_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_path = sys.argv[2]

    print(f"--- KeyShot DXF Import Automation ---")
    print(f"Importing: {dxf_path}")

    # 1. Clean Scene (optional, usually start with new file)
    lux.newScene()

    # 2. Setup Environment
    setup_environment()

    # 3. Import DXF
    opts = lux.getImportOptions("dxf")
    if opts:
        opts["snap_to_ground"] = True
        opts["automatic_gamma"] = True
        opts["center_geometry"] = True
        lux.importFile(dxf_path, opts=opts)
    else:
        lux.importFile(dxf_path)

    # 4. Apply Materials
    apply_materials()

    # 5. Scene Polish
    # Enable Ground Reflections for premium look
    lux.setGroundReflections(True)
    
    # 6. Render
    print(f"Rendering to: {output_path}...")
    
    # Render Options
    ropts = lux.getRenderOptions()
    ropts.addToQueue = False
    
    # Execute render
    # Resolution 1920x1080 typical
    lux.renderImage(output_path, width=1920, height=1080, opts=ropts)
    
    print(f"--- KeyShot Automation Finished ---")

if __name__ == "__main__":
    main()
