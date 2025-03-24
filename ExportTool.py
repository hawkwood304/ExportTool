from shiboken2 import wrapInstance

import os
import maya.cmds as cm
# import pymel.core as pm
import maya.OpenMaya as oMaya
import maya.OpenMayaUI as oMayaUI

from PySide2 import QtWidgets, QtCore, QtGui
from maya.mel import eval

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# import sys


class QHLine(QtWidgets.QFrame):

    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(self.HLine)
        self.setFrameShadow(self.Sunken)


class QVLine(QtWidgets.QFrame):

    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(self.VLine)
        self.setFrameShadow(self.Sunken)


class QHLineName(QtWidgets.QGridLayout):

    def __init__(self, name):
        super(QHLineName, self).__init__()
        name_lb = QtWidgets.QLabel(name)
        name_lb.setAlignment(QtCore.Qt.AlignCenter)
        name_lb.setStyleSheet("font: italic 9pt;" "color: azure;")
        self.addWidget(name_lb, 0, 0, 1, 1)
        self.addWidget(QHLine(), 0, 1, 1, 2)


# noinspection PyAttributeOutsideInit
class ExportTool(QtWidgets.QWidget):
    fbxVersions = {
        '2016': 'FBX201600',
        '2014': 'FBX201400',
        '2013': 'FBX201300',
        '2017': 'FBX201700',
        '2018': 'FBX201800',
        '2019': 'FBX201900'
    }

    def __init__(self):
        super(ExportTool, self).__init__()

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.file_path_lb = QtWidgets.QLabel("File path: ")
        self.file_path_le = QtWidgets.QLineEdit()

        self.select_file_path_btn = QtWidgets.QPushButton('')
        self.select_file_path_btn.setIcon(QtGui.QIcon(':fileOpen.png'))
        self.select_file_path_btn.setToolTip('Select File')

        self.shot_name_lb = QtWidgets.QLabel("Shot name: ")
        self.shot_name_le = QtWidgets.QLineEdit()

        self.object_name_lb = QtWidgets.QLabel("Object name: ")
        self.object_name_le = QtWidgets.QLineEdit()

        self.cam_name_lb = QtWidgets.QLabel("Cam name:")
        self.cam_name_le = QtWidgets.QLineEdit()
        self.cam_name_btn = QtWidgets.QPushButton("Assign")

        self.star_time_lb = QtWidgets.QLabel("Start: ")
        self.star_time_le = QtWidgets.QLineEdit()
        self.end_time_lb = QtWidgets.QLabel("End: ")
        self.end_time_le = QtWidgets.QLineEdit()

        self.offset_lb = QtWidgets.QLabel("Time Offset:")
        self.offset_spinbox = QtWidgets.QSpinBox()
        self.offset_spinbox.setRange(0, 100)  # Allow up to 100 frames of offset
        self.offset_spinbox.setValue(0)  # Default to 0

        self.bake_cb = QtWidgets.QCheckBox("Bake Animation")
        self.bake_cb.setChecked(True)
        self.fbxVersion_combobox = QtWidgets.QComboBox()
        for fbxVersion in sorted(self.fbxVersions):
            self.fbxVersion_combobox.addItem(fbxVersion)
            self.fbxVersion_combobox.setCurrentText("2019")

        self.fbx_export_btn = QtWidgets.QPushButton("FBX Export")
        self.fbx_export_btn.setStyleSheet(
            'QPushButton {background-color: lightyellow; color: black;}'
        )

        self.abc_mesh_name_lb = QtWidgets.QLabel("Char name: ")
        self.abc_mesh_name_le = QtWidgets.QLineEdit()

        self.export_all_btn = QtWidgets.QPushButton("Export All")
        self.export_all_btn.setStyleSheet(
            'QPushButton {background-color: lightyellow; color: black;}'
        )

        self.abc_export_btn = QtWidgets.QPushButton("ABC Export")
        self.abc_export_btn.setStyleSheet(
            'QPushButton {background-color: lightyellow; color: black;}'
        )

    def create_layouts(self):
        file_option_layout = QtWidgets.QGridLayout()
        file_option_layout.addWidget(self.file_path_lb, 0, 0)
        file_option_layout.addWidget(self.file_path_le, 0, 1)
        file_option_layout.addWidget(self.select_file_path_btn, 0, 2)

        scene_option_layout = QtWidgets.QGridLayout()
        scene_option_layout.addWidget(self.shot_name_lb, 0, 0, 1, 1)
        scene_option_layout.addWidget(self.shot_name_le, 0, 1, 1, 2)

        scene_option_layout.addWidget(self.object_name_lb, 1, 0, 1, 1)
        scene_option_layout.addWidget(self.object_name_le, 1, 1, 1, 2)
        scene_option_layout.addWidget(self.cam_name_lb, 2, 0, 1, 1)
        scene_option_layout.addWidget(self.cam_name_le, 2, 1, 1, 1)
        scene_option_layout.addWidget(self.cam_name_btn, 2, 2, 1, 1)

        time_option_layout = QtWidgets.QVBoxLayout()
        time_layout = QtWidgets.QHBoxLayout()
        time_layout.addWidget(self.star_time_lb)
        time_layout.addWidget(self.star_time_le)
        time_layout.addWidget(self.end_time_lb)
        time_layout.addWidget(self.end_time_le)
        time_layout.addWidget(self.offset_lb)
        time_layout.addWidget(self.offset_spinbox)

        time_option_layout.addLayout(time_layout)

        fbx_option_layout = QtWidgets.QHBoxLayout()
        fbx_option_layout.addWidget(self.bake_cb)
        fbx_option_layout.addWidget(self.fbxVersion_combobox)
        fbx_option_layout.addWidget(self.fbx_export_btn)

        abc_export_layout = QtWidgets.QHBoxLayout()
        abc_export_layout.addWidget(self.abc_mesh_name_lb)
        abc_export_layout.addWidget(self.abc_mesh_name_le)
        abc_export_layout.addWidget(self.abc_export_btn)

        export_all_layout = QtWidgets.QHBoxLayout()
        export_all_layout.addWidget(self.export_all_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(QHLineName("File option"))
        main_layout.addLayout(file_option_layout)
        main_layout.addLayout(QHLineName("Scene option"))
        main_layout.addLayout(scene_option_layout)
        main_layout.addLayout(QHLineName("Time option"))
        main_layout.addLayout(time_option_layout)
        main_layout.addLayout(QHLineName("Fbx option"))
        main_layout.addLayout(fbx_option_layout)
        main_layout.addLayout(QHLineName("Abc option"))
        main_layout.addLayout(abc_export_layout)
        main_layout.addLayout(QHLineName("Export All"))
        main_layout.addLayout(export_all_layout)

    def create_connections(self):
        self.select_file_path_btn.clicked.connect(self.show_file_select_dialog)
        self.fbx_export_btn.clicked.connect(self.fbx_export)
        self.cam_name_btn.clicked.connect(self.assign_cam_button)
        self.abc_export_btn.clicked.connect(self.abc_export)
        self.export_all_btn.clicked.connect(self.export_all)

    @staticmethod
    def execute_mel_command(command):
        try:
            eval(command)
            # logger.info(f"MEL command executed: {command}")
        except RuntimeError as e:
            logger.error(f"Failed to execute MEL command: {command} - {e}")

    def fbx_export_option(self, path, min_time, max_time):
        fbx_version = self.fbxVersion_combobox.currentText()
        version = self.fbxVersions[fbx_version]

        self.execute_mel_command("FBXExportSmoothingGroups -v true")
        self.execute_mel_command("FBXExportHardEdges -v false")
        self.execute_mel_command("FBXExportTangents -v false")
        self.execute_mel_command("FBXExportSmoothMesh -v true")
        self.execute_mel_command("FBXExportInstances -v false")
        self.execute_mel_command("FBXExportReferencedAssetsContent -v false")

        if self.bake_cb.isChecked():
            self.execute_mel_command('FBXExportBakeComplexAnimation -v true')
            self.execute_mel_command("FBXExportBakeComplexStep -v 1")
            self.execute_mel_command("FBXExportBakeComplexStart -v {}".format(min_time))
            self.execute_mel_command("FBXExportBakeComplexEnd -v {}".format(max_time))
        else:
            self.execute_mel_command('FBXExportBakeComplexAnimation -v false')

        self.execute_mel_command("FBXExportUseSceneName -v false")
        self.execute_mel_command("FBXExportQuaternion -v euler")
        self.execute_mel_command("FBXExportShapes -v true")
        self.execute_mel_command("FBXExportSkins -v true")

        # Constraints
        self.execute_mel_command("FBXExportConstraints -v false")
        # Cameras
        self.execute_mel_command("FBXExportCameras -v true")
        # Lights
        self.execute_mel_command("FBXExportLights -v true")
        # Embed Media
        self.execute_mel_command("FBXExportEmbeddedTextures -v false")
        # Connections
        self.execute_mel_command("FBXExportInputConnections -v true")
        # Axis Conversion
        self.execute_mel_command("FBXExportUpAxis y")
        # Version
        self.execute_mel_command('FBXExportFileVersion -v {}'.format(version))

        # Export!

        self.execute_mel_command('FBXExport -f "{0}" -s'.format(path))

    def assign_cam_button(self):
        """
        Assigns selected cameras from the Maya scene to the tool's camera name field.

        This function checks for selected objects in the Maya scene and filters out any non-camera objects.
        If no cameras are found or if nothing is selected, appropriate errors are logged and displayed.
        """
        try:
            # Get the currently selected objects in the Maya scene
            selected_objects = cm.ls(selection=True)
            if not selected_objects:
                oMaya.MGlobal.displayError("Please select at least one camera.")
                return

            # Filter out cameras from the selected objects
            selected_cameras = []
            for obj in selected_objects:
                # Check if the object or its children are cameras
                obj_children = cm.listRelatives(obj, children=True, fullPath=True) or []
                for child in obj_children or [obj]:
                    if cm.objectType(child) == 'camera':
                        selected_cameras.append(obj)
                        break  # Only add the first valid camera per object

            if not selected_cameras:
                # Log and display an error if no cameras were found in the selection
                logger.warning("No cameras selected or found in the selected objects.")
                oMaya.MGlobal.displayError("No cameras detected in the selected objects.")
                return

            # Format the list of selected cameras as a comma-separated string
            formatted_cameras = ", ".join(selected_cameras)
            self.cam_name_le.setText(formatted_cameras)

            # Log the successful assignment of cameras
            logger.info(f"Assigned cameras: {formatted_cameras}")

        except Exception as e:
            logger.error(f"Unexpected error in assign_cam_button: {e}")
            oMaya.MGlobal.displayError(f"Error occurred while assigning cameras: {e}")

    def get_list_camera_name(self):
        """
        Fetches and returns a cleaned list of camera names from the input field.

        Returns:
            list: A list of camera names if valid input exists.
                  An empty list if the input is empty or invalid.
        """
        # Get raw input from the camera name field
        raw_input = self.cam_name_le.text().strip()

        if raw_input:
            # Clean the input by removing unnecessary spaces and splitting by commas
            camera_names = [name.strip() for name in raw_input.split(",") if name.strip()]

            # Log and return the cleaned list of camera names
            if camera_names:
                logger.info(f"Camera names extracted: {camera_names}")
                return camera_names
            else:
                logger.warning("Input contains only whitespace or invalid camera names.")
                return []
        else:
            logger.warning("Camera name input is empty.")
            return []

    def show_file_select_dialog(self):
        self.file_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select directory')

        self.file_path_le.setText(self.file_path)

    def get_convert_file_path(self):
        """
        Converts the input file path to a normalized format and validates its existence.

        Returns:
            str: The converted file path with forward slashes if it exists.
            None: If the file path doesn't exist, displays an error and returns None.
        """
        # Get the raw file path from the input field
        raw_path = self.file_path_le.text().strip()

        if raw_path:
            # Normalize the file path (replace backslashes with forward slashes)
            normalized_path = raw_path.replace("\\", "/")

            # Check if the directory exists
            if os.path.isdir(normalized_path):
                logger.info(f"Valid file path: {normalized_path}")
                return normalized_path
            else:
                logger.error(f"File path does not exist: {normalized_path}")
                oMaya.MGlobal.displayError("File path doesn't exist. Please select a valid directory.")
                return None
        else:
            logger.warning("File path input is empty.")
            oMaya.MGlobal.displayError("File path cannot be empty.")
            return None

    def get_shot_name(self):
        """
        Assign shot name for this scene

        Returns:
            Shot name(str)
        """

        shot_name = self.shot_name_le.text()
        if len(shot_name) == 0:
            logger.error("Shot name is empty")
            return oMaya.MGlobal_displayError("Shot name can't be empty")
        return shot_name

    def get_list_character_name(self):
        """
        Fetches a cleaned list of character names from the input field.

        Returns:
            list: A list of character names (if input exists). An empty list if input is empty.
        """
        # Get raw input
        raw_input = self.object_name_le.text()

        if raw_input:
            # Clean input by stripping unnecessary spaces and splitting by commas
            character_names = [name.strip() for name in raw_input.split(",") if name.strip()]

            # Return cleaned list
            if character_names:
                logger.info(f"Character names extracted: {character_names}")
                return character_names
            else:
                logger.warning("Input contains only whitespace or invalid data.")
                return []
        else:
            logger.warning("Character name input is empty.")
            return []

    def get_list_abc_mesh_name(self):
        """
        Fetches a cleaned list of Alembic mesh names from the input field.

        Returns:
            list: A list of mesh names (if input exists). An empty list if input is empty or contains only invalid data.
        """
        # Get raw input
        raw_input = self.abc_mesh_name_le.text()

        if raw_input:
            # Clean input by stripping unnecessary spaces and splitting by commas
            mesh_names = [name.strip() for name in raw_input.split(",") if name.strip()]

            # Return cleaned list
            if mesh_names:
                logger.info(f"Alembic mesh names extracted: {mesh_names}")
                return mesh_names
            else:
                logger.warning("Alembic mesh name input contains only whitespace or invalid data.")
                return []
        else:
            logger.warning("Alembic mesh name input is empty.")
            return []

    def get_time_range(self):
        """
        Get the start frame, end frame, and apply any applicable offset.

        Returns:
            tuple: (start_frame, end_frame) as integers.
        """
        try:
            # Fetch default start and end times from Maya
            min_time = int(cm.playbackOptions(q=True, min=True))
            max_time = int(cm.playbackOptions(q=True, max=True))

            # Override with user-provided start and end times if they exist
            if self.star_time_le.text():
                try:
                    min_time = int(self.star_time_le.text())
                except ValueError:
                    logger.error("Invalid Start Frame value provided.")
                    oMaya.MGlobal.displayError("Start time must be a valid integer.")
                    return None, None

            if self.end_time_le.text():
                try:
                    max_time = int(self.end_time_le.text())
                except ValueError:
                    logger.error("Invalid End Frame value provided.")
                    oMaya.MGlobal.displayError("End time must be a valid integer.")
                    return None, None

            # Apply offset from spin box
            offset_frames = self.offset_spinbox.value()
            min_time -= offset_frames
            max_time += offset_frames

            logger.info(f"Computed Time Range: Start = {min_time}, End = {max_time}")
            return min_time, max_time

        except Exception as e:
            logger.error(f"Unexpected error in get_time_range: {e}")
            oMaya.MGlobal.displayError(f"An error occurred while determining the time range: {e}")
            return None, None

    def export_camera(self, camera, export_dir, shot_name, min_time, max_time):
        """
        Exports baked animation data for the specified camera to an FBX file.

        Args:
            camera (str): The camera to export.
            export_dir (str): The output directory for the FBX file.
            shot_name (str): The shot name (prefix for file output).
            min_time (int): Start frame to bake animations.
            max_time (int): End frame to bake animations.

        """
        try:
            # Prepare camera export settings
            cam_shapes = cm.listRelatives(camera, shapes=True)
            new_cam = cm.camera()
            mult_matrix_node = cm.createNode("multMatrix", name="cam_multMatrix")
            decompose_matrix_node = cm.createNode("decomposeMatrix", name="cam_decomposeMatrix")
            cm.connectAttr(f"{camera}.worldMatrix[0]", f"{mult_matrix_node}.matrixIn[0]")
            cm.connectAttr(f"{mult_matrix_node}.matrixSum", f"{decompose_matrix_node}.inputMatrix")
            cm.connectAttr(f"{decompose_matrix_node}.outputTranslate", f"{new_cam[0]}.translate")
            cm.connectAttr(f"{decompose_matrix_node}.outputRotate", f"{new_cam[0]}.rotate")

            # Connect focal length
            cm.connectAttr(f"{cam_shapes[0]}.focalLength", f"{new_cam[1]}.focalLength", force=True)

            # Bake animation for translation, rotation, and focal length
            self.bake_camera_animation(new_cam, min_time, max_time)

            # Export FBX
            cam_filename = f"{shot_name}_cam.fbx" if len(self.get_list_camera_name()) == 1 else f"{camera}_cam.fbx"
            cam_output_path = os.path.join(export_dir, cam_filename).replace(os.sep, '/')
            self.fbx_export_option(cam_output_path, min_time, max_time)

            # Clean up: delete temporary camera and nodes
            cm.delete(new_cam[0], mult_matrix_node, decompose_matrix_node)
            logger.info(f"Exported camera {camera} to {cam_output_path}")

        except Exception as e:
            logger.error(f"Failed to export camera '{camera}': {e}")
            oMaya.MGlobal.displayError(f"Error exporting camera '{camera}': {e}")

    def bake_camera_animation(self, new_cam, min_time, max_time):
        """
        Bakes animation for the camera's position and focal length.

        Args:
            new_cam (list): The new camera created for baking.
            min_time (int): Start frame.
            max_time (int): End frame.

        """
        try:
            # Bake translation and rotation data
            cm.select(new_cam[0])
            self.execute_mel_command(
                f'bakeResults -simulation true -t "{min_time}:{max_time}" -sampleBy 1 -oversamplingRate 1 '
                f'-disableImplicitControl true -preserveOutsideKeys true -sparseAnimCurveBake false '
                f'-removeBakedAttributeFromLayer false -removeBakedAnimFromLayer false -bakeOnOverrideLayer false '
                f'-minimizeRotation true -controlPoints false -shape false;'
            )

            # Bake focal length data
            cm.select(f"{new_cam[1]}.focalLength")
            self.execute_mel_command(
                f'bakeResults -simulation true -t "{min_time}:{max_time}" -sampleBy 1 -oversamplingRate 1 '
                f'-disableImplicitControl true -preserveOutsideKeys true -sparseAnimCurveBake false '
                f'-removeBakedAttributeFromLayer false -removeBakedAnimFromLayer false -bakeOnOverrideLayer false '
                f'-minimizeRotation true -controlPoints false -shape true;'
            )

            # Shift animation keys to start from frame 1
            cm.keyframe(new_cam[0], edit=True, relative=True, timeChange=-min_time)
        except Exception as e:
            logger.error(f"Failed to bake camera animation: {e}")
            raise

    @staticmethod
    def collect_namespaces(character_names):
        """
        Collects namespaces for the specified characters.

        Args:
            character_names (list): List of characters to look up namespaces.

        Returns:
            list: A list of unique namespaces matching the character names.

        """
        namespaces_raw = cm.ls()
        namespaces = set()
        for item in namespaces_raw:
            if "DeformationSystem" in item or "ExportGrp" in item:
                ns = item.rpartition(":")[0]
                char_name_define = item.split(":")
                if len(char_name_define) == 1:
                    char_name = char_name_define[0]
                else:
                    char_name = char_name_define[-2]

                for character in character_names:
                    if character in char_name:
                        namespaces.add(ns)
        return list(namespaces)

    def export_characters(self, character_names, export_dir, shot_name, min_time, max_time):
        """
        Exports FBX files for characters based on namespace definitions.

        Args:
            character_names (list): List of character names to export.
            export_dir (str): The output directory for FBX files.
            shot_name (str): The shot name to use in filenames.
            min_time (int): Start frame.
            max_time (int): End frame.

        """
        try:
            namespaces = self.collect_namespaces(character_names)

            for character in character_names:
                char_namespaces = [ns for ns in namespaces if character in ns]
                for idx, char_ns in enumerate(char_namespaces):
                    filename = f"{shot_name}_{character}_anim.fbx" if len(
                        char_namespaces) == 1 else f"{shot_name}_{character}_{idx + 1}_anim.fbx"
                    output_path = os.path.join(export_dir, filename).replace(os.sep, '/')

                    # Select and export: prioritize ExportGrp > DeformationSystem
                    if cm.objExists(f"{char_ns}:ExportGrp"):
                        cm.select(f"{char_ns}:ExportGrp")
                    elif cm.objExists(f"{char_ns}:DeformationSystem"):
                        cm.select(f"{char_ns}:DeformationSystem", f"{char_ns}:Geometry")
                    else:
                        logger.warning(
                            f"No valid group found for character {character} in namespace {char_ns}. Skipping...")
                        continue

                    self.fbx_export_option(output_path, min_time, max_time)

        except Exception as e:
            logger.error(f"Failed to export characters: {e}")
            oMaya.MGlobal.displayError(f"Error exporting characters: {e}")

    def fbx_export(self):
        """
        Handles the FBX export process for selected characters, cameras, and namespaces.
        Exports animation, baked data, or entire scenes into the specified directory.

        Requirements:
            - The target directory must exist and be writable.
            - Object names should be properly formatted and namespaces correctly set up.

        """
        try:
            # Get configured paths, settings, and time ranges
            filepath = self.get_convert_file_path()
            shot_name = self.get_shot_name()
            character_names = self.get_list_character_name()
            min_time, max_time = self.get_time_range()
            cameras = self.get_list_camera_name()

            # Ensure file path and shot name are valid
            if not filepath or not shot_name:
                logger.error("File path or shot name is not provided.")
                return

            # Create the export directory
            export_dir = os.path.join(filepath, shot_name).replace(os.sep, '/')
            export_dir = str(export_dir)
            if not os.path.isdir(export_dir):
                os.mkdir(export_dir)

            # Handle camera export
            if cameras:
                for camera in cameras:
                    self.export_camera(camera, export_dir, shot_name, min_time, max_time)

            # Handle character export
            self.export_characters(character_names, export_dir, shot_name, min_time, max_time)

        except RuntimeError as e:
            logger.error(f"Runtime error encountered during FBX export: {e}")
            oMaya.MGlobal.displayError(f"FBX export failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during FBX export: {e}")
            oMaya.MGlobal.displayError(f"Error: {e}")

    def abc_export(self):
        """
        Exports Alembic (.abc) files for the characters based on selected Alembic export groups and
        the provided input settings (time range, character names, and shot name).

        The exported files are saved in the specified directory as defined in the tool's fields.
        """
        try:
            # Get file path, shot name, character names, and time range
            export_dir = self.get_convert_file_path()
            shot_name = self.get_shot_name()
            character_names = self.get_list_abc_mesh_name()
            min_time, max_time = self.get_time_range()

            # Ensure export directory exists or create it
            if not export_dir or not shot_name:
                logger.error("Export directory or shot name is invalid.")
                oMaya.MGlobal.displayError("Export directory or shot name is invalid. Please check your inputs.")
                return
            export_dir = os.path.join(export_dir, shot_name).replace(os.sep, '/')
            if not os.path.isdir(export_dir):
                os.mkdir(export_dir)

            # Collect namespaces containing DeformationSystem for the specified characters
            namespaces = []
            all_scene_items = cm.ls()
            for item in all_scene_items:
                if "ABCExport" in item:
                    namespace = item.rpartition(":")[0]
                    char_name_define_list = item.split(":")
                    if len(char_name_define_list) == 1:
                        char_name_define = char_name_define_list[0]
                    else:
                        char_name_define = char_name_define_list[-2]

                    for char_name in character_names:
                        if char_name in char_name_define:
                            namespaces.append(namespace)

            namespaces = list(set(namespaces))  # Remove duplicates

            if not namespaces:
                # Handle empty namespace list
                logger.warning("No valid namespaces found for the specified characters.")
                oMaya.MGlobal.displayWarning("No valid Alembic export groups found for the specified character names.")
                return

            # Export Alembic files for each character namespace
            for namespace in namespaces:
                if cm.objExists(f"{namespace}:ABCExport"):
                    for char_name in character_names:
                        if char_name in namespace:
                            # Prepare file name and path
                            file_name = f"{shot_name}_{char_name}_anim.abc"
                            file_path = os.path.join(export_dir, file_name).replace(os.sep, '/')

                            # Export range and root setup
                            cm.select(f"{namespace}:ABCExport")
                            root_object = cm.ls(sl=True, long=True)[0]
                            root = f"-root {root_object}"

                            # Build Alembic export command
                            command = (
                                f"-frameRange {min_time} {max_time} -stripNamespaces -uvWrite -writeFaceSets "
                                f"-wholeFrameGeo -worldSpace -writeUVSets {root} -file {file_path}"
                            )

                            # Execute Alembic export
                            cm.AbcExport(j=command)
                            logger.info(f"Exported Alembic file: {file_path}")

            oMaya.MGlobal.displayInfo("Alembic export completed successfully.")

        except RuntimeError as e:
            logger.error(f"Alembic export runtime error: {e}")
            oMaya.MGlobal.displayError(f"Alembic export failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during Alembic export: {e}")
            oMaya.MGlobal.displayError(f"Unexpected error during Alembic export: {e}")

    def export_all(self):
        """
        Combines the FBX and Alembic export processes.

        This function handles the export of all elements, ensuring both FBX and Alembic exports
        are executed sequentially. Any errors that occur in one process will not prevent the other
        process from running. Logs detailed progress and errors for both operations.
        """
        try:
            # Begin the export process
            logger.info("Starting the export process for all elements.")

            # Perform FBX export
            try:
                logger.info("Starting FBX export...")
                self.fbx_export()
                logger.info("FBX export completed successfully.")
            except Exception as e:
                logger.error(f"FBX export failed: {e}")
                oMaya.MGlobal.displayError(f"FBX export encountered an error: {e}")

            # Perform Alembic export
            try:
                logger.info("Starting Alembic export...")
                self.abc_export()
                logger.info("Alembic export completed successfully.")
            except Exception as e:
                logger.error(f"Alembic export failed: {e}")
                oMaya.MGlobal.displayError(f"Alembic export encountered an error: {e}")

            # Notify completion
            oMaya.MGlobal.displayInfo("Export All process completed.")

        except Exception as e:
            logger.error(f"Unexpected error in export_all: {e}")
            oMaya.MGlobal.displayError(f"An unexpected error occurred during Export All: {e}")


# noinspection PyMethodMayBeStatic,PyAttributeOutsideInit,PyMethodOverriding
class MainWindow(QtWidgets.QDialog):
    """
    Main Window for the Export Tool.

    Handles the GUI display, geometry management, and interaction between the tool
    and the main Maya window.
    """
    WINDOW_TITLE = "Export Tool"

    # Directories for user scripts and icons
    SCRIPTS_DIR = cm.internalVar(userScriptDir=True)
    ICON_DIR = os.path.join(SCRIPTS_DIR, 'Thi/Icon')

    dlg_instance = None

    @classmethod
    def display(cls):
        """
        Displays the main dialog window. Reuses the single instance if it already exists.
        """
        if not cls.dlg_instance:
            cls.dlg_instance = MainWindow()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    @classmethod
    def maya_main_window(cls):
        """
        Retrieves the main Maya window widget.

        Returns:
            QWidget: The main Maya window as a Python object.
        """
        try:
            main_window_ptr = oMayaUI.MQtUtil.mainWindow()
            return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
        except Exception as e:
            logger.error(f"Failed to retrieve Maya main window: {e}")
            return None

    def __init__(self):
        """
        Initializes the MainWindow instance.
        """
        super(MainWindow, self).__init__(self.maya_main_window())
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        # Geometry management
        self.geometry = None

        # Set window size restrictions
        self.setMinimumSize(400, 500)
        self.setMaximumSize(400, 500)

        # Create the UI elements
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        """
        Initializes the widgets in the main window.
        """
        self.export_tool = ExportTool()  # Main export tool widget
        self.close_btn = QtWidgets.QPushButton("Close")

    def create_layouts(self):
        """
        Arranges the widgets in the main window.
        """
        # Layout for the "Close" button
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.close_btn)

        # Main layout for the window
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.export_tool)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        """
        Connects signals and slots for the widgets.
        """
        self.close_btn.clicked.connect(self.close)

    def showEvent(self, event):
        """
        Handles the "show" event for the window. Restores the saved geometry.

        Args:
            event (QShowEvent): The show event.
        """
        super(MainWindow, self).showEvent(event)
        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, event):
        """
        Handles the "close" event for the window. Saves the current geometry.

        Args:
            event (QCloseEvent): The close event.
        """
        super(MainWindow, self).closeEvent(event)
        self.geometry = self.saveGeometry()