import sys
import os
import ezdxf
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax2, gp_Vec
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCC.Core.AIS import AIS_Shape
from OCC.Core.Quantity import Quantity_NOC_BLACK, Quantity_NOC_WHITE, Quantity_NOC_STEELBLUE, Quantity_NOC_ORANGE, Quantity_NOC_GREEN, Quantity_NOC_GRAY50
from OCC.Core.V3d import V3d_View
from OCC.Core.Aspect import Aspect_TOL_SOLID
from OCC.Display.SimpleGui import init_display

def get_layer_properties(layer_name):
    """Returns (color, height) based on the layer name."""
    layer_name = layer_name.upper()
    if 'STRUCT_WALLS' in layer_name:
        return Quantity_NOC_WHITE, 100.0
    elif 'SHELVES' in layer_name:
        return Quantity_NOC_STEELBLUE, 60.0
    elif 'RETAIL_ISLANDS' in layer_name:
        return Quantity_NOC_ORANGE, 40.0
    elif 'CHECKOUT' in layer_name:
        return Quantity_NOC_GREEN, 30.0
    elif 'PILLARS' in layer_name:
        return Quantity_NOC_GRAY50, 120.0
    else:
        return Quantity_NOC_WHITE, 1.0

def import_dxf_to_occt(dxf_path):
    """Parses DXF and builds 3D shapes for each entity."""
    if not os.path.exists(dxf_path):
        print(f"Error: File not found {dxf_path}")
        return []

    try:
        doc = ezdxf.readfile(dxf_path)
    except Exception as e:
        print(f"Error reading DXF: {e}")
        return []

    msp = doc.modelspace()
    shapes = []

    # Simple grouping of entities by layer to form wires
    # (DXF often has separate lines for a rectangle)
    layer_entities = {}
    for e in msp.query('LINE'):
        layer = e.dxf.layer
        if layer not in layer_entities:
            layer_entities[layer] = []
        layer_entities[layer].append(e)

    for layer, entities in layer_entities.items():
        color, height = get_layer_properties(layer)
        
        for e in entities:
            try:
                # Create 3D points
                start = gp_Pnt(e.dxf.start.x, e.dxf.start.y, 0.0)
                end = gp_Pnt(e.dxf.end.x, e.dxf.end.y, 0.0)
                
                # Make edge
                edge = BRepBuilderAPI_MakeEdge(start, end).Edge()
                
                # Extrude edge to Face if it's a 2D line (for walls, etc.)
                # But typically we want a solid. Let's make a vertical ribbon first.
                vec = gp_Vec(0, 0, height)
                prism = BRepPrimAPI_MakePrism(edge, vec).Shape()
                
                shapes.append((prism, color))
            except Exception as ex:
                print(f"Failed to process entity: {ex}")

    return shapes

def render_scene(shapes, output_path):
    """Sets up AIS context and renders the scene to a file."""
    # Using pythonocc-core's SimpleGui as a helper to get a view
    # In a real batch pipeline, we'd use V3d_View directly without a GUI window.
    # But for a robust demo, SimpleGui is often more reliable on different OSs.
    
    display, start_display, add_menu, add_function_to_menu = init_display()
    
    # Configure Premium View
    display.View.SetBgGradientColors(Quantity_NOC_BLACK, Quantity_NOC_GRAY50, 2, True)
    display.View.SetAntialiasingOn()
    
    # Display Shapes
    for shape, color in shapes:
        ais_shape = AIS_Shape(shape)
        ais_shape.SetColor(color)
        display.Context.Display(ais_shape, True)

    # Set Camera - Isometric style
    display.View_Isometric()
    display.FitAll()
    
    # Zoom out a bit for spacing
    display.View.SetZoom(0.8)
    
    # Force redraw
    display.View.Redraw()
    
    # Dump to PNG
    print(f"Dumping view to {output_path}...")
    success = display.View.Dump(output_path)
    if success:
        print("Successfully rendered!")
    else:
        print("Failed to dump view.")
    
    # Note: start_display() would open the window and block.
    # For automation, we just exit after Dump.
    # sys.exit(0)

def main():
    if len(sys.argv) < 3:
        print("Usage: python renderer.py <input.dxf> <output.png>")
        return

    dxf_path = sys.argv[1]
    output_path = sys.argv[2]
    
    print(f"Loading DXF: {dxf_path}...")
    shapes = import_dxf_to_occt(dxf_path)
    
    if not shapes:
        print("No shapes to render.")
        return

    print(f"Found {len(shapes)} shapes. Rendering...")
    render_scene(shapes, output_path)

if __name__ == "__main__":
    main()
