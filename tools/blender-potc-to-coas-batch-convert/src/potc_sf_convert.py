import argparse
import os
import sys

import bpy

_BATCH_CONVERT_DIR = os.path.abspath(__file__).replace('\\','/').split('/')[:-1]
_GM_IMPORT_DIR = os.path.join(_BATCH_CONVERT_DIR[0], os.sep,*_BATCH_CONVERT_DIR[1:-2] + ['blender-gm-import', 'io_import_gm'])
sys.path.append(_GM_IMPORT_DIR)
_GM_EXPORT_DIR = os.path.join(_BATCH_CONVERT_DIR[0], os.sep,*_BATCH_CONVERT_DIR[1:-2] + ['blender-gm-export', 'io_export_gm'])
sys.path.append(_GM_EXPORT_DIR)

# # Native packages
import import_gm
import export_gm


class bckgrnd_import_gm(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "storm.import_gm"
    bl_label = "Import COAS gm in the background"

    def __init__(self):    
        self.filepath = 'D:/Maelstrom/games/new-horizons/RESOURCE/MODELS/Characters/33_Affrica.gm'
        self.textures_path = 'D:/Maelstrom/games/new-horizons/RESOURCE/Textures/Characters/spa_adm_18_2.tga.tx'
        self.an_name = 'woman_coas.an'
        self.an_path = 'D:/Maelstrom/games/new-horizons-convert/RESOURCE/animation/woman_coas.an'
        self.fix_coas_man_head = False
        self.convert_coas_to_potc_man = False
        self.convert_potc_to_coas_man = False
        self.convert_coas_to_potc_woman = False
        self.convert_potc_to_coas_woman = True

    def execute(self, context):
        an_path = os.path.join(os.path.dirname(self.filepath), self.an_name)
        textures_path = os.path.join(os.path.dirname(self.filepath), self.textures_path)
        if os.path.isfile(an_path):
            return import_gm.import_gm(
                context,
                self.filepath,
                textures_path=self.textures_path,
                an_path=self.an_path,
                fix_coas_man_head=self.fix_coas_man_head,
                convert_coas_to_potc_man=self.convert_coas_to_potc_man,
                convert_potc_to_coas_man=self.convert_potc_to_coas_man,
                convert_coas_to_potc_woman=self.convert_coas_to_potc_woman,
                convert_potc_to_coas_woman=self.convert_potc_to_coas_woman,
                report_func=self.report
            )

        return import_gm.import_gm(context, self.filepath, textures_path=self.textures_path, report_func=self.report)


class bckgrnd_export_gm(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "storm.export_gm"
    bl_label = "Export COAS gm in the background"

    def __init__(self):    
        self.filepath = 'D:/33_Affrica.gm'
        self.BSP = False

    def execute(self, context):
        return export_gm.export_gm(context, self.filepath, self.BSP)



def register():
    bpy.utils.register_class(bckgrnd_import_gm)
    bpy.utils.register_class(bckgrnd_export_gm)


def unregister():
    bpy.utils.unregister_class(bckgrnd_import_gm)
    bpy.utils.unregister_class(bckgrnd_export_gm)


if __name__ == "__main__":
    register()

    print('running script')

    # test call
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    bpy.ops.storm.import_gm()
    
    print('select')
    bpy.ops.object.select_all(action='DESELECT')

    objectToSelect = bpy.data.objects["root"]
    objectToSelect.select_set(True)    
    bpy.context.view_layer.objects.active = objectToSelect

    print('export')
    bpy.ops.storm.export_gm()    