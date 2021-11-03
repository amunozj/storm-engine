import argparse
import os
import sys

import bpy
from bpy.props import BoolProperty, StringProperty

_BATCH_CONVERT_DIR = os.path.abspath(__file__).replace('\\','/').split('/')[:-1]
_GM_IMPORT_DIR = os.path.join(_BATCH_CONVERT_DIR[0], os.sep,*_BATCH_CONVERT_DIR[1:-2] + ['blender-gm-import', 'io_import_gm'])
sys.path.append(_GM_IMPORT_DIR)
_GM_EXPORT_DIR = os.path.join(_BATCH_CONVERT_DIR[0], os.sep,*_BATCH_CONVERT_DIR[1:-2] + ['blender-gm-export', 'io_export_gm'])
sys.path.append(_GM_EXPORT_DIR)

# # Native packages
import import_gm
import export_gm

parser = argparse.ArgumentParser()
parser.add_argument(
    '--nh_dir',
    type=str,
    default=None,
    required=True,
    help='Location of the New Horizons mod'
)

parser.add_argument(
    '--output_dir',
    type=str,
    default=None,
    required=True,
    help='Folder for converted output'
)

class bckgrnd_import_gm(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "storm.import_gm"
    bl_label = "Import COAS gm in the background"

    filepath_in: StringProperty(
        name="Path to file to convert",
        description="Path to textures (relative or absolute)",
        default="filepath"
    )

    textures_path: StringProperty(
        name="Textures path",
        description="Path to textures (relative or absolute)",
        default="textures"
    )

    an_path: StringProperty(
        name="Animation path",
        description="Path to animation file",
        default="animation"
    )

    fix_coas_man_head: BoolProperty(
        name="Fix CoAS man skeleton head",
        default=False
    )

    convert_coas_to_potc_man: BoolProperty(
        name="Convert CoAS man skeleton to PotC",
        default=False
    )

    convert_potc_to_coas_man: BoolProperty(
        name="Convert PotC man skeleton to CoAS",
        default=False
    )

    convert_coas_to_potc_woman: BoolProperty(
        name="Convert CoAS woman skeleton to PotC",
        default=False
    )

    convert_potc_to_coas_woman: BoolProperty(
        name="Convert PotC woman skeleton to CoAS",
        default=False
    )

    def execute(self, context):
        if os.path.isfile(self.an_path):
            return import_gm.import_gm(
                context,
                self.filepath_in,
                textures_path=self.textures_path,
                an_path=self.an_path,
                fix_coas_man_head=self.fix_coas_man_head,
                convert_coas_to_potc_man=self.convert_coas_to_potc_man,
                convert_potc_to_coas_man=self.convert_potc_to_coas_man,
                convert_coas_to_potc_woman=self.convert_coas_to_potc_woman,
                convert_potc_to_coas_woman=self.convert_potc_to_coas_woman,
                report_func=self.report
            )

        return import_gm.import_gm(context, self.filepath_in, textures_path=self.textures_path, report_func=self.report)


class bckgrnd_export_gm(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "storm.export_gm"
    bl_label = "Export COAS gm in the background"

    filepath_out: StringProperty(
        name="Path to converted file",
        description="Path to output file",
        default="filepath out"
    )    

    def execute(self, context):
        return export_gm.export_gm(context, self.filepath_out, False)


def register():
    bpy.utils.register_class(bckgrnd_import_gm)
    bpy.utils.register_class(bckgrnd_export_gm)


def unregister():
    bpy.utils.unregister_class(bckgrnd_import_gm)
    bpy.utils.unregister_class(bckgrnd_export_gm)


class storm_model:
    """
    Model class to store a dictionary with all the necessary parameters as well
        as flags to indicate gender and processing status
    """

    def __init__(self, model_list,
                nh_dir=None,
                output_dir=None):
        """
        Initialization function of the storm_model class

        Parameters
        ----------
        model_list: list
            list with all entries read from initModel.c
        nh_dir: str
            Location of the New Horizons mod
        output_dir: str
            Folder for converted output                   
        """

        self.nh_dir = nh_dir
        self.output_dir = output_dir
        self.comments_and_ending = [line for line in model_list if ('model.' not in line) or '//' in line.split('model.')[0] or 'AssignModel' in line or 'IF' in line]
        self.only_parameters = [line for line in model_list if ('model.' in line) and '//' not in line.split('model.')[0] and 'AssignModel' not in line]
        self.model_parameters = {}

        # Fill parameter dictionary
        for line in self.only_parameters:
            parameter = line.split('model.')[1].split('=')[0].replace(' ', '').replace('\t', '')
            self.model_parameters[parameter] = line.split('=')[1].replace('\t', '').strip()
        
        # Make sure the model has an assigned sex
        if 'sex' not in self.model_parameters:
            self.model_parameters['sex'] = '"man";'

        # Store flag to indicate that the model has already been converted
        self.coas_ready = False
        if 'ani' in self.model_parameters:
            self.coas_ready = 'coas' in self.model_parameters['ani']

        # Assemble model file name
        self.model_file = self.model_parameters['id'].split('"')[1] + ".gm"

        # clean sex string
        if 'woman' in self.model_parameters['sex']:
            self.sex = 'woman'
        elif 'man' in self.model_parameters['sex']:
            self.sex = 'man'
        else:
            self.sex = 'None'

        # Define parameters for import
        self.filepath = self.nh_dir + f'/RESOURCE/MODELS/Characters/{self.model_file}'
        self.textures_path = self.nh_dir + '/RESOURCE/Textures/Characters/'

        self.convert_potc_to_coas_man=False
        self.convert_potc_to_coas_woman=False
        if self.sex == 'woman':
            self.convert_potc_to_coas_woman = True
        elif self.sex == 'man':
            self.convert_potc_to_coas_man = True

        self.an_path = self.output_dir + f'/RESOURCE/animation/{self.sex}_coas.an'
        self.fix_coas_man_head = False
        self.convert_coas_to_potc_man = False
        self.convert_coas_to_potc_woman = False

        # Define parameters for export
        self.filepath_out = self.output_dir + f'/RESOURCE/MODELS/Characters/{self.model_file}'


    def print_to_file(self, initModelsOutputFile):
        """
        Function to print model into file

        Parameters
        ----------
        initModelsOutputFile: file
            file where to print the lines of each model       
        """

        for key, value in self.model_parameters.items():
            initModelsOutputFile.write(f'\tmodel.{key} = {value}\n')

        for line in self.comments_and_ending:
            initModelsOutputFile.write(line)


def potc_coas_batch_convert(
    nh_dir=None,
    output_dir=None
    ):
    """Batch process initModels.c

    Parameters
    ----------
    nh_dir: str
        Location of the New Horizons mod
    output_dir: str
        Folder for converted output
    """

    register()

    initModelsFile = nh_dir + '/PROGRAM/Models/initModels.c'
    initModelsFile = open(initModelsFile, 'r')
    initModelslines = initModelsFile.readlines()

    if not os.path.exists(output_dir + '/PROGRAM/Models/'):
        os.makedirs(output_dir + '/PROGRAM/Models/')
    if not os.path.exists(output_dir + '/RESOURCE/MODELS/Characters/'):
        os.makedirs(output_dir + '/RESOURCE/MODELS/Characters/')

    initModelsOutputFile = output_dir + '/PROGRAM/Models/initModels.c'
    initModelsOutputFile = open(initModelsOutputFile, 'w')
    

    model_definition_start = False
    model_found = False
    block_comment_found = False
    for index, line in enumerate(initModelslines):

        # Find where the all the models start to be defined and trigger flag
        if not model_definition_start:
            initModelsOutputFile.write(line)

            if 'MODEL_HIGH = 0;' in line:
                model_definition_start = True
                model_found = False
                block_comment_found = False
        
        else:

            # Find if there is a block comment and simply transliterate
            if not block_comment_found:

                if '/*' in line:
                    initModelsOutputFile.write(line)
                    block_comment_found = True

                else:

                    # Find where the model begings and trigger flag
                    if not model_found:

                        # Begin list of lines associated with a model
                        if 'model.description' in line:
                            model_found = True
                            model_list = [line]
                        else:
                            initModelsOutputFile.write(line)
                    
                    # Append lines unitl the last line of the model is found
                    else:
                        model_list += [line]

                        # Close the model, trigger conversion, and print to file
                        if 'AddCharacterModel(model);' in line:
                            model_found = False
                            model = storm_model(model_list, nh_dir, output_dir)
                            if not model.coas_ready and model.sex is not 'None':
                                bpy.ops.object.select_all(action='SELECT')
                                bpy.ops.object.delete()

                                # Import
                                print(model.filepath, model.textures_path, model.an_path, model.fix_coas_man_head, model.convert_coas_to_potc_man, model.convert_potc_to_coas_man, model.convert_coas_to_potc_woman, model.convert_potc_to_coas_woman)
                                bpy.ops.storm.import_gm(filepath_in=model.filepath, 
                                                        textures_path=model.textures_path,
                                                        an_path=model.an_path,
                                                        fix_coas_man_head=model.fix_coas_man_head,
                                                        convert_coas_to_potc_man=model.convert_coas_to_potc_man,
                                                        convert_potc_to_coas_man=model.convert_potc_to_coas_man,
                                                        convert_coas_to_potc_woman=model.convert_coas_to_potc_woman,
                                                        convert_potc_to_coas_woman=model.convert_potc_to_coas_woman)

                                # Select
                                objectToSelect = bpy.data.objects["root"]
                                objectToSelect.select_set(True)    
                                bpy.context.view_layer.objects.active = objectToSelect

                                # Export
                                bpy.ops.storm.export_gm(filepath_out=model.filepath_out)
                                model.model_parameters['ani'] = f'"{model.sex}_coas";'
                            model.print_to_file(initModelsOutputFile)

            else:
                initModelsOutputFile.write(line)
                if '*/' in line:
                    block_comment_found = False


    initModelsFile.close()
    initModelsOutputFile.close()
    unregister()


if __name__ == "__main__":

    print(sys.argv[sys.argv.index("--")+1:])

    print(parser.parse_known_args(sys.argv[sys.argv.index("--")+1:]))
    args = vars(parser.parse_known_args(sys.argv[sys.argv.index("--")+1:])[0])
    print(args)

    potc_coas_batch_convert(**args)