import bpy
import sys

with open("test_out.log", "w") as f:
    f.write("Testing extension installation...\n")
    try:
        if hasattr(bpy.context.preferences.system, 'use_online_access'):
            f.write("Enabling online access...\n")
            bpy.context.preferences.system.use_online_access = True
            
        f.write("Syncing repos...\n")
        bpy.ops.extensions.repo_sync_all()
        f.write("Installing io_import_dxf...\n")
        bpy.ops.extensions.package_install(repo_index=0, pkg_id="io_import_dxf")
        f.write("Successfully installed via extensions!\n")
        
        import addon_utils
        addon_utils.enable("io_import_dxf")
        f.write("Enabled addon\n")
    except Exception as e:
        f.write(f"Error: {e}\n")
