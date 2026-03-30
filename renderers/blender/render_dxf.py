import bpy
import os
import sys
import math
import mathutils
import subprocess
import argparse

# Ensure pip installs to a controllable local directory
local_lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv_libs")
if local_lib_dir not in sys.path:
    sys.path.insert(0, local_lib_dir)

try:
    import ezdxf
except ImportError:
    print("Installing ezdxf locally for Blender Python...")
    subprocess.check_call([sys.executable, "-m", "ensurepip"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ezdxf", "--target", local_lib_dir])
    import site
    import importlib
    import ezdxf

def clean_scene():
    """Clears the existing scene or starts fresh."""
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    for block in bpy.data.meshes: bpy.data.meshes.remove(block)
    for block in bpy.data.materials: bpy.data.materials.remove(block)
    for block in bpy.data.cameras: bpy.data.cameras.remove(block)
    for block in bpy.data.lights: bpy.data.lights.remove(block)
    for block in bpy.data.curves: bpy.data.curves.remove(block)

def get_or_create_dxf_material(doc, entity, args):
    """Dynamically creates or retrieves a Blender material based on DXF properties."""
    
    # Base defaults
    color = (0.5, 0.5, 0.5, 1.0)
    roughness = 0.5
    metallic = 0.0
    alpha = 1.0
    mat_key = "Mat"
    
    # 1. Evaluate Color mapping
    if args.color:
        aci = 7 # Default ACI
        if entity.dxf.hasattr('color'):
            aci = entity.dxf.color
            
        if aci == 256: # BYLAYER
            layer_obj = doc.layers.get(entity.dxf.layer)
            if layer_obj:
                aci = layer_obj.color
                
        # Handle BYBLOCK or complex by leaving default ACI 7
        if aci == 0 or aci == 256: aci = 7
        
        try:
            from ezdxf.colors import int2rgb
            r, g, b = int2rgb(aci)
            color = (r/255.0, g/255.0, b/255.0, 1.0)
        except Exception:
            pass
            
        mat_key += f"_C{aci}"
    else:
        mat_key += "_NoColor"
        
    # 2. Evaluate Material / Transparency mapping
    if args.material:
        # Real DXF transparency check
        if entity.dxf.hasattr('transparency'):
            alpha = 0.5 # Simplified generic transparency mapping
            mat_key += "_Transp"
            
        # Semantic mapping based on standard architecture layers
        # as pure DXF material handles are often missing or proprietary
        layer_name = entity.dxf.layer.upper()
        if 'GLASS' in layer_name or 'WINDOW' in layer_name:
            alpha = 0.3
            roughness = 0.1
            metallic = 0.1
            mat_key += "_Glass"
        elif 'METAL' in layer_name or 'SHELVES' in layer_name or 'CHECKOUT' in layer_name:
            metallic = 0.8
            roughness = 0.2
            mat_key += "_Metal"
        elif 'WALL' in layer_name:
            roughness = 0.9
            mat_key += "_Wall"
    else:
        mat_key += "_NoMat"

    # Specific override for TEXT to ensure readability if not fully overridden by user
    if entity.dxftype() in ('TEXT', 'MTEXT'):
        mat_key += "_TEXT"
        if not args.color:
            color = (1.0, 0.8, 0.1, 1.0) # Golden default for text
        if not args.material:
            roughness = 0.3
            metallic = 0.2
            
    # Lookup Cache
    if mat_key in bpy.data.materials:
        return bpy.data.materials[mat_key]
        
    # Create new material
    mat = bpy.data.materials.new(name=mat_key)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    
    if alpha < 1.0:
        mat.blend_method = 'BLEND'
        bsdf.inputs["Alpha"].default_value = alpha
        
    return mat

def create_box_data(verts_list, faces_list, start_pos, end_pos, z_start, z_end, thickness_dir, out_extent):
    """Helper to append a box to vertex/face lists."""
    v_idx = len(verts_list)
    px_vec = (thickness_dir[0] * out_extent, thickness_dir[1] * out_extent, 0)
    
    # 8 vertices
    b = [
        (start_pos[0] + px_vec[0], start_pos[1] + px_vec[1], z_start),
        (start_pos[0] - px_vec[0], start_pos[1] - px_vec[1], z_start),
        (end_pos[0]   - px_vec[0], end_pos[1]   - px_vec[1], z_start),
        (end_pos[0]   + px_vec[0], end_pos[1]   + px_vec[1], z_start),
        
        (start_pos[0] + px_vec[0], start_pos[1] + px_vec[1], z_end),
        (start_pos[0] - px_vec[0], start_pos[1] - px_vec[1], z_end),
        (end_pos[0]   - px_vec[0], end_pos[1]   - px_vec[1], z_end),
        (end_pos[0]   + px_vec[0], end_pos[1]   + px_vec[1], z_end),
    ]
    verts_list.extend(b)
    
    f = [
        (v_idx+0, v_idx+1, v_idx+2, v_idx+3), (v_idx+4, v_idx+7, v_idx+6, v_idx+5),
        (v_idx+0, v_idx+3, v_idx+7, v_idx+4), (v_idx+1, v_idx+5, v_idx+6, v_idx+2),
        (v_idx+0, v_idx+4, v_idx+5, v_idx+1), (v_idx+3, v_idx+2, v_idx+6, v_idx+7)
    ]
    faces_list.extend(f)

def create_line_mesh(obj_name, start_pos, end_pos, height, thickness, mat, layer_type):
    """Creates a 3D mesh. Makes shelves if layer_type implies it, else solid box."""
    dx = end_pos.x - start_pos.x
    dy = end_pos.y - start_pos.y
    length = math.sqrt(dx*dx + dy*dy)
    if length < 0.001: return None
        
    ux = dx / length
    uy = dy / length
    px = -uy
    py = ux
    
    verts = []
    faces = []
    
    start = (start_pos.x, start_pos.y)
    end = (end_pos.x, end_pos.y)
    thick_dir = (px, py)

    if 'SHELV' in layer_type or 'ISLAND' in layer_type:
        # Create a double-sided realistic supermarket shelf!
        num_shelves = 4 if 'SHELV' in layer_type else 3
        shelf_thickness = 0.2
        shelf_spacing = height / num_shelves
        
        # Center divider (Thin board in the middle)
        create_box_data(verts, faces, start, end, 0.0, height, thick_dir, thickness * 0.05)
        
        # Bottom kickplate (Thick block at the ground)
        create_box_data(verts, faces, start, end, 0.0, 0.5, thick_dir, thickness * 0.45)
        
        # Render individual shelves
        for i in range(1, num_shelves + 1):
            z_level = i * shelf_spacing
            if i == num_shelves: # Top cover
                z_level = height - shelf_thickness
            
            # Shelf platters sticking out on both sides
            create_box_data(verts, faces, start, end, z_level, z_level + shelf_thickness, thick_dir, thickness * 0.5)
            
    else:
        # Standard block for walls, checkout, pillars
        create_box_data(verts, faces, start, end, 0.0, height, thick_dir, thickness / 2.0)
    
    mesh_data = bpy.data.meshes.new(name=f"Mesh_{obj_name}")
    mesh_data.from_pydata(verts, [], faces)
    mesh_data.update()
    
    mesh_obj = bpy.data.objects.new(obj_name, mesh_data)
    bpy.context.collection.objects.link(mesh_obj)
    mesh_data.materials.append(mat)
    return mesh_obj

def create_text_object(obj_name, text_str, pos, base_height, rotation_deg, thickness, shadow, mat):
    """Creates 3D text in Blender with smart auto-rotation, length-aware scaling, custom thickness, and shadow depth."""
    font_curve = bpy.data.curves.new(type="FONT", name=f"FontCurve_{obj_name}")
    font_curve.body = text_str
    
    font_curve.align_x = 'CENTER'
    font_curve.align_y = 'CENTER'
    
    # offset behaves like 2D bolding/thickness
    font_curve.offset = thickness
    # extrude behaves like a 3D shadow depth/extrusion
    font_curve.extrude = shadow 
    
    font_obj = bpy.data.objects.new(obj_name, font_curve)
    
    # 1. SMART ROTATION (Only 0 or 90 based on requested behavior)
    final_rot = 0.0
    if 45 < abs(rotation_deg % 180) < 135:
        final_rot = 90.0
    
    # 2. SMART SCALING (Consistent height, but shrink slightly for long text)
    length = len(text_str)
    scale_factor = 1.0
    if length > 8:
        scale_factor = max(0.6, 1.0 - (length - 8) * 0.05)
    
    final_h = base_height * scale_factor
    
    font_obj.location = (pos.x, pos.y, 15.1)
    font_obj.rotation_euler[2] = math.radians(final_rot)
    font_obj.scale = (final_h, final_h, final_h)
    
    bpy.context.collection.objects.link(font_obj)
    font_curve.materials.append(mat)
    return font_obj

def import_dxf_manually(dxf_path, args):
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    objects = []
    
    scale = args.unit_scale
            
    for e in msp:
        layer = getattr(e.dxf, 'layer', 'DEFAULT').upper()
        
        # Dynamically evaluate material/color based on DXF and CLI flags
        mat = get_or_create_dxf_material(doc, e, args)

        if e.dxftype() == 'LINE':
            handle = getattr(e.dxf, 'handle', 'NO_HANDLE')
            obj_name = f"LINE_{layer}_{handle}"
            
            # Hardcoded vertical structural heights in Blender Units (assumes meters)
            height, thickness = 2.0, 1.0 * scale
            if 'STRUCT_WALLS' in layer: height, thickness = 10.0, 5.0 * scale
            elif 'SHELVES' in layer: height, thickness = 6.0, 3.0 * scale
            elif 'PILLARS' in layer: height, thickness = 12.0, 4.0 * scale
            elif 'RETAIL_ISLANDS' in layer: height, thickness = 4.0, 3.0 * scale
            elif 'CHECKOUT' in layer: height, thickness = 3.0, 4.0 * scale
            elif 'AISLES' in layer: height, thickness = 0.5, 8.0 * scale
            
            class Pos: pass
            start_p = Pos(); start_p.x = e.dxf.start.x * scale; start_p.y = e.dxf.start.y * scale
            end_p = Pos(); end_p.x = e.dxf.end.x * scale; end_p.y = e.dxf.end.y * scale
            
            line_obj = create_line_mesh(obj_name, start_p, end_p, height, thickness, mat, layer)
            if line_obj: objects.append(line_obj)
            
        elif e.dxftype() == 'LWPOLYLINE':
            handle = getattr(e.dxf, 'handle', 'NO_HANDLE')
            
            height = 2.0
            if 'STRUCT_WALLS' in layer: height = 10.0
            elif 'SHELVES' in layer: height = 6.0
            elif 'PILLARS' in layer: height = 12.0
            elif 'RETAIL_ISLANDS' in layer: height = 4.0
            elif 'CHECKOUT' in layer: height = 3.0
            elif 'AISLES' in layer: height = 0.5
            
            width = getattr(e.dxf, 'const_width', 5.0) * scale
            if width <= 0: width = 5.0 * scale
            
            pts = list(e.vertices())
            for i in range(len(pts) - 1):
                p1, p2 = pts[i], pts[i+1]
                obj_name = f"POLY_{layer}_{handle}_{i}"
                
                class Pos: pass
                start_p = Pos(); start_p.x = p1[0] * scale; start_p.y = p1[1] * scale
                end_p = Pos(); end_p.x = p2[0] * scale; end_p.y = p2[1] * scale
                
                line_obj = create_line_mesh(obj_name, start_p, end_p, height, width, mat, layer)
                if line_obj: objects.append(line_obj)
            
            if getattr(e.dxf, 'closed', False) and len(pts) > 2:
                p1, p2 = pts[-1], pts[0]
                obj_name = f"POLY_{layer}_{handle}_closed"
                
                class Pos: pass
                start_p = Pos(); start_p.x = p1[0] * scale; start_p.y = p1[1] * scale
                end_p = Pos(); end_p.x = p2[0] * scale; end_p.y = p2[1] * scale
                
                line_obj = create_line_mesh(obj_name, start_p, end_p, height, width, mat, layer)
                if line_obj: objects.append(line_obj)
                
        elif e.dxftype() in ('TEXT', 'MTEXT'):
            handle = getattr(e.dxf, 'handle', 'NO_HANDLE')
            text_str = getattr(e.dxf, 'text', '')
            dxf_pos = getattr(e.dxf, 'insert', mathutils.Vector((0,0,0)))
            
            class Pos: pass
            pos = Pos()
            pos.x = dxf_pos.x * scale
            pos.y = dxf_pos.y * scale
            
            obj_name = f"TEXT_{layer}_{handle}"
            
            # Smart Orientation: Check DXF rotation
            orig_rot = getattr(e.dxf, 'rotation', 0.0) 
            
            # Use Command Line Arguments for scaling and thickness
            text_obj = create_text_object(
                obj_name, text_str, pos, 
                args.text_size, orig_rot, args.text_thickness, args.text_shadow,
                mat
            )
            objects.append(text_obj)
            
    return objects

def setup_lighting():
    bpy.context.scene.world.use_nodes = True
    bg_node = bpy.context.scene.world.node_tree.nodes['Background']
    bg_node.inputs[0].default_value = (0.02, 0.02, 0.04, 1.0)
    
    bpy.ops.object.light_add(type='SUN', location=(100, -100, 300))
    sun = bpy.context.active_object
    sun.data.energy = 5.0
    sun.rotation_euler = (math.radians(50), 0, math.radians(45))
    
    bpy.ops.object.light_add(type='AREA', location=(400, 300, 500))
    area = bpy.context.active_object
    area.data.size = 1000.0
    area.data.energy = 5000000.0 
    area.rotation_euler = (0, 0, 0)

def get_dxf_bounds(dxf_path, scale):
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')
    
    found = False
    for e in msp:
        if e.dxftype() == 'LINE':
            found = True
            min_x = min(min_x, e.dxf.start.x * scale, e.dxf.end.x * scale)
            min_y = min(min_y, e.dxf.start.y * scale, e.dxf.end.y * scale)
            max_x = max(max_x, e.dxf.start.x * scale, e.dxf.end.x * scale)
            max_y = max(max_y, e.dxf.start.y * scale, e.dxf.end.y * scale)
        elif e.dxftype() == 'LWPOLYLINE':
            found = True
            for pt in e.vertices():
                min_x = min(min_x, pt[0] * scale)
                min_y = min(min_y, pt[1] * scale)
                max_x = max(max_x, pt[0] * scale)
                max_y = max(max_y, pt[1] * scale)
        elif e.dxftype() in ('TEXT', 'MTEXT'):
            found = True
            pos = getattr(e.dxf, 'insert', mathutils.Vector((0,0,0)))
            min_x = min(min_x, pos.x * scale)
            min_y = min(min_y, pos.y * scale)
            max_x = max(max_x, pos.x * scale)
            max_y = max(max_y, pos.y * scale)
            
    if not found:
        return 0, 800 * scale, 0, 600 * scale
    return min_x, max_x, min_y, max_y

def setup_camera(min_x, max_x, min_y, max_y, args):
    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    bpy.context.scene.camera = cam

    # Use arguments for clipping
    cam.data.clip_end = args.clip_end
    cam.data.clip_start = 0.1

    print(f"DXF Bounds: X({min_x} to {max_x}), Y({min_y} to {max_y})")

    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    width = max_x - min_x
    height = max_y - min_y
    
    size = max(width, height)
    distance = size * args.cam_dist
    if distance < 10: distance = 100
    
    yaw_rad = math.radians(args.cam_yaw)
    pitch_rad = math.radians(args.cam_pitch)
    
    # Distance is hypotenuse
    z = distance * math.sin(pitch_rad)
    ground_dist = distance * math.cos(pitch_rad)
    
    x = center_x + ground_dist * math.sin(yaw_rad)
    y = center_y - ground_dist * math.cos(yaw_rad)
    
    cam.location = (x, y, z)
    
    direction = mathutils.Vector((center_x, center_y, 0)) - cam.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()

def main():
    argv = sys.argv
    if "--" not in argv:
        args_list = []
    else:
        args_list = argv[argv.index("--") + 1:]
        
    parser = argparse.ArgumentParser()
    parser.add_argument("dxf_path", help="Path to DXF input file")
    parser.add_argument("output_path", help="Path to PNG output file")
    parser.add_argument("--clip-end", type=float, default=100000.0, help="Camera far clipping distance")
    parser.add_argument("--cam-dist", type=float, default=1.5, help="Camera distance multiplier relative to scene size")
    parser.add_argument("--cam-pitch", type=float, default=45.0, help="Camera pitch angle (0 to 90)")
    parser.add_argument("--cam-yaw", type=float, default=20.0, help="Camera yaw angle (-180 to 180)")
    
    # NEW ARGUMENTS FOR TEXT
    parser.add_argument("--text-size", type=float, default=12.0, help="Base height of text labels")
    parser.add_argument("--text-thickness", type=float, default=0.0, help="2D Fatness/Thickness of 3D text labels (offset)")
    parser.add_argument("--text-shadow", type=float, default=0.2, help="Thickness/Shadow depth of 3D text labels (extrusion)")
    
    # NEW ARGUMENT FOR UNIT SCALING
    parser.add_argument("--unit-scale", type=float, default=1.0, help="Multiply DXF coordinates by this factor (e.g. 0.01 for cm to meters)")

    # NEW ARGUMENTS FOR DYNAMIC RENDERING
    parser.add_argument("--color", action="store_true", help="Parse and apply colors from DXF entities instead of default gray")
    parser.add_argument("--material", action="store_true", help="Parse and apply materials/transparency from DXF entities")

    if not args_list:
        parser.print_help()
        return
        
    args = parser.parse_args(args_list)

    clean_scene()

    min_x, max_x, min_y, max_y = get_dxf_bounds(args.dxf_path, args.unit_scale)
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    size = max(max_x - min_x, max_y - min_y) * 2

    # Ground
    bpy.ops.mesh.primitive_plane_add(size=size, location=(center_x, center_y, -0.1))
    ground = bpy.context.active_object
    ground.name = "Ground"
    mat_ground = bpy.data.materials.new(name="GroundMat")
    bsdf = mat_ground.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.2, 0.2, 0.25, 1.0) 
    bsdf.inputs["Roughness"].default_value = 0.5
    ground.data.materials.append(mat_ground)

    objects = import_dxf_manually(args.dxf_path, args)

    setup_lighting()
    setup_camera(min_x, max_x, min_y, max_y, args)

    bpy.context.scene.render.filepath = args.output_path
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080
    
    print(f"Rendering to {args.output_path}...")
    bpy.ops.render.render(write_still=True)

if __name__ == "__main__":
    main()
