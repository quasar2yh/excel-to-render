import bpy

try:
    if hasattr(bpy.context.preferences.system, 'use_online_access'):
        bpy.context.preferences.system.use_online_access = True
    bpy.ops.extensions.repo_sync_all()
    bpy.ops.extensions.package_install(repo_index=0, pkg_id="io_import_dxf")
except Exception:
    pass

import addon_utils
addon_utils.enable("io_import_dxf", default_set=True)

with open("test_ops.log", "w") as f:
    try:
        f.write("import_scene ops: " + str(dir(bpy.ops.import_scene)) + "\n")
    except Exception as e:
        f.write("error import_scene: " + str(e) + "\n")
    try:
        f.write("import_dxf ops: " + str(dir(bpy.ops.import_dxf)) + "\n")
    except Exception as e:
        f.write("error import_dxf: " + str(e) + "\n")
