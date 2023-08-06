# -*- coding: utf-8 -*-
"""A interface for contextcapture."""

# Import built-in models
from __future__ import print_function
from __future__ import unicode_literals

import hashlib
import logging
import os
import sys
import time
import base64
import xml.etree.ElementTree as ET
from builtins import str

from dayan_contextcapture.constants import PACKAGE_NAME
from dayan_contextcapture import Analyze
from rayvision_log import init_logger
from dayan_contextcapture import constants
from rayvision_utils import utils
from rayvision_utils.exception import tips_code
from rayvision_utils.exception.exception import AnalyseFailError, CGFileNotExistsError

VERSION = sys.version_info[0]


class AnalyzeContextCapture(object):
    def __init__(self, xml_file="", project_name="", cg_file=r"G:\workspace",
                 photo_group_path=None, kml_file="", world_coord_sys="", render_software="ContextCapture",
                 output_type=None, sensor_size="", local_os=None, platform="54", workspace=None,
                 is_many_at="0", many_at=None,
                 is_submit_pos="0", pos_info=None, pos_scope=None,
                 tile_mode="0", is_set_origin_coord="0", origin_coord=None,
                 is_set_offset_coord="0", offset_coord=None,
                 logger=None,
                 log_folder=None,
                 log_name=None,
                 log_level="DEBUG"
                 ):
        """Initialize and examine the analysis information.

        Args:
            xml_file (str): The XML path.
            project_name (str): The project name.
            cg_file (str): The input path of photos.
            photo_group_path (str): The photo group path of photos'list.
            kml_file (str): KML File.
            world_coord_sys (str): worldCoordSys.
            render_software (str): render software.
            output_type (List): example: ["OSGB","OBJ","LAS","Cesium 3D Tiles","TIFF","Editable OBJ","3MX","FBX","S3C"]
            sensor_size (str): the sensor size of camera
            platform (str): Platform num.
            logger (object, optional): Custom log object.
            log_folder (str, optional): Custom log save location.
            log_name (str, optional): Custom log file name.
            log_level (string):  Set log level, example: "DEBUG","INFO","WARNING","ERROR".
        """

        self.logger = logger
        if not self.logger:
            init_logger(PACKAGE_NAME, log_folder, log_name)
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(level=log_level.upper())

        self.xml_file = xml_file
        self.kml_file = kml_file
        self.project_name = project_name
        self.cg_file = cg_file
        self.photo_group_path = photo_group_path
        self.platform = platform
        self.render_software = render_software
        self.world_coord_sys = world_coord_sys
        self.output_type = output_type
        self.sensor_size = sensor_size
        self.tile_mode = tile_mode
        self.is_set_origin_coord = is_set_origin_coord
        self.is_set_offset_coord = is_set_offset_coord
        self.origin_coord = origin_coord
        self.offset_coord = offset_coord
        self.is_submit_pos = is_submit_pos
        self.pos_info = pos_info
        self.pos_scope = pos_scope
        self.is_many_at = is_many_at
        self.many_at = many_at

        local_os = self.check_local_os(local_os)
        self.local_os = local_os
        self.tmp_mark = str(int(time.time()))
        workspace = os.path.join(self.check_workspace(workspace),
                                 self.tmp_mark)
        if not os.path.exists(workspace):
            os.makedirs(workspace)
        self.workspace = workspace
        if self.kml_file:
            self.check_path(self.kml_file)

        self.task_json = os.path.join(workspace, "task.json")
        self.tips_json = os.path.join(workspace, "tips.json")
        self.asset_json = os.path.join(workspace, "asset.json")
        self.upload_json = os.path.join(workspace, "upload.json")
        self.tips_info = {}
        self.task_info = {}
        self.asset_info = {}
        self.upload_info = {}

    @staticmethod
    def check_path(tmp_path):
        """Check if the path exists."""
        if not os.path.exists(tmp_path):
            raise CGFileNotExistsError("{} is not found".format(tmp_path))

    def add_tip(self, code, info):
        """Add error message.

        Args:
            code (str): error code.
            info (str or list): Error message description.

        """
        if isinstance(info, str):
            self.tips_info[code] = [info]
        elif isinstance(info, list):
            self.tips_info[code] = info
        else:
            raise Exception("info must a list or str.")

    def save_tips(self):
        """Write the error message to tips.json."""
        utils.json_save(self.tips_json, self.tips_info, ensure_ascii=False)

    @staticmethod
    def check_local_os(local_os):
        """Check the system name.

        Args:
            local_os (str): System name.

        Returns:
            str

        """
        if not local_os:
            if "win" in sys.platform.lower():
                local_os = "windows"
            else:
                local_os = "linux"
        return local_os

    def check_workspace(self, workspace):
        """Check the working environment.

        Args:
            workspace (str):  Workspace path.

        Returns:
            str: Workspace path.

        """
        if not workspace:
            if self.local_os == "windows":
                workspace = os.path.join(os.environ["USERPROFILE"], "dayan_sdk")
            else:
                workspace = os.path.join(os.environ["HOME"], "dayan_sdk")
        return workspace

    def write_task_json(self):
        """The initialization task.json."""
        constants.TASK_INFO["task_info"]["input_cg_file"] = self.cg_file.replace("\\", "/")
        constants.TASK_INFO["task_info"]["input_project_path"] = ""
        constants.TASK_INFO["task_info"]["render_layer_type"] = "0"
        constants.TASK_INFO["task_info"]["project_name"] = self.project_name
        constants.TASK_INFO["task_info"]["cg_id"] = "2017"
        constants.TASK_INFO["task_info"]["os_name"] = "1" if self.local_os == "windows" else "0"
        constants.TASK_INFO["task_info"]["platform"] = self.platform
        constants.TASK_INFO["task_info"]["ram"] = "32"
        constants.TASK_INFO["software_config"] = {
            "plugins": {},
            "cg_version": "",
            "os_name": "1",
            "cg_name": self.render_software
        }

        constants.TASK_INFO["scene_info"] = {
            "contrl_point": {},
            "param": {
                "lockRange": 0 if self.kml_file else 1,
                "tileMode": self.tile_mode,
                "worldCoordSys": self.world_coord_sys,
                "rangeFile": {
                    "fileName": self.kml_file,
                    "fileSize": os.path.getsize(self.kml_file) if self.kml_file else '',
                    "fileContent": self.get_file_base64(self.kml_file) if self.kml_file else ''},
                "tileSize": "",
                "outputType": self.output_type
            },
            "blocks": [],
            "blocks_info": [
                {
                    "file_path": self.xml_file
                }
            ],
            "group": {
                "job_type": 1 if self.xml_file else 0,
                "pic_count": 0,
                "groups": [
                ],
                "project_name": self.project_name,
                "total_pixel": ""
            }
        }
        if self.is_set_origin_coord is "1":
            constants.TASK_INFO["scene_info"]['param'].update({
                "originCoord": {
                    "coord_z": self.origin_coord['coord_z'],
                    "coord_x": self.origin_coord['coord_x'],
                    "coord_y": self.origin_coord['coord_y']
                }})

        if self.is_set_offset_coord is "1":
            constants.TASK_INFO["scene_info"]['param'].update({
                "offsetCoord": {
                    "coord_z": self.offset_coord['coord_z'],
                    "coord_x": self.offset_coord['coord_x'],
                    "coord_y": self.offset_coord['coord_y']
                }})

        scene_info_group = constants.TASK_INFO["scene_info"]['group']
        for path in self.photo_group_path:
            info = Analyze.check_photogroup(path)
            photo_info = info[0]
            if self.is_submit_pos is "1":
                if self.pos_scope['is_all'] is "1":
                    pos = {
                        "field_order": self.pos_info['field_order'],
                        "file_path": self.pos_info['file_path'],
                        "ignore_lines": self.pos_info['ignore_lines'],
                        "splite_char": self.pos_info['splite_char'],
                        "coord_system": self.pos_info['coord_system']
                    }
                else:
                    pos = self.get_pos_info(path)
            else:
                pos = {}

            scene_info_group['groups'].append({
                "pic_count": photo_info['pic_count'],
                "pic_width": photo_info['pic_width'],
                "focal_length": photo_info['focal_length'],
                "pic_height": photo_info['pic_height'],
                "group_name": os.path.basename(path),
                "group_id": "",
                "sensor_size": self.sensor_size,
                "pos_info": pos,
                "group_path": path,
                "total_pixel": int(photo_info['pic_width']) * int(photo_info['pic_height']) * int(
                    photo_info['pic_count']),
                "camera_producter": photo_info['camera_producter'],
                "camera_model": photo_info['camera_model'],
            })
        # 分块空三
        if self.is_many_at is "1":
            many_at = {
                "kmls": [],
                "block_merge": self.many_at['block_merge']
            }
            id = "0"
            for at in self.many_at['kmls']:
                many_at['kmls'].append({
                    "total_pixel": "",
                    "content": self.get_file_base64(at['file_path']),
                    "fileSize": "",
                    "kml_id": f'{id}',
                    "kml_name": at['file_path']
                })
                id = int(id) + 1
            constants.TASK_INFO["many_at"] = many_at
        scene_info_group['pic_count'], scene_info_group['total_pixel'] = self.count_pic_info(scene_info_group['groups'])
        utils.json_save(self.task_json, constants.TASK_INFO)

    def count_pic_info(self, groups):
        """Compute the number of picture and total pixel."""
        pic = 0
        pixel = 0
        for group in groups:
            pic += group['pic_count']
            pixel += group['total_pixel']
        return pic, pixel

    def get_pos_info(self, ph_path):
        pos = {}
        assert len(self.pos_scope['scope']) != 0, "请填写对应pos文件路径！"

        for ph in self.pos_scope['scope']:
            if ph == ph_path:
                pos = {
                    "field_order": self.pos_info['field_order'],
                    "file_path": self.pos_info['file_path'],
                    "ignore_lines": self.pos_info['ignore_lines'],
                    "splite_char": self.pos_info['splite_char'],
                    "coord_system": self.pos_info['coord_system']
                }
        return pos

    def write_asset_json(self):
        """Generate the asset.json."""
        for ph_path in self.photo_group_path:
            photo_files = os.listdir(ph_path)
            for file in photo_files:
                if not (file.endswith('.JPG') or file.endswith('.JPEG')):
                    continue
                constants.ASSET_INFO['asset'].append(os.path.join(ph_path, file))
        constants.ASSET_INFO['block_files'] = self.xml_file.replace("\\", "/")
        if self.is_submit_pos is "1":
            constants.ASSET_INFO['pos_file'] = self.pos_info['file_path'].replace("\\", "/")
        utils.json_save(self.asset_json, constants.ASSET_INFO)

    def write_upload_json(self):
        """Generate the upload.json."""
        self.upload_info["asset"] = []

        for ph_path_f in self.photo_group_path:
            photo_files = os.listdir(ph_path_f)
            for file in photo_files:
                if not (file.endswith('.JPG') or file.endswith('.JPEG')):
                    continue
                ph_path = os.path.join(ph_path_f, file)
                self.upload_info["asset"].append({
                    "local": ph_path.replace("\\", "/"),
                    "server": utils.convert_path(ph_path)
                })
        if self.xml_file:
            self.upload_info["asset"].append({
                "local": self.xml_file.replace("\\", "/"),
                "server": utils.convert_path(self.xml_file)
            })
            constants.UPLOAD_INFO['block_files'] = {
                "local": self.xml_file.replace("\\", "/"),
                "server": utils.convert_path(self.xml_file)
            }

        if self.is_submit_pos is "1":
            constants.UPLOAD_INFO['pos_file'] = {
                "local": self.pos_info['file_path'].replace("\\", "/"),
                "server": utils.convert_path(self.pos_info['file_path'])
            }
            # for upload
            self.upload_info["asset"].append({
                "local": self.pos_info['file_path'].replace("\\", "/"),
                "server": utils.convert_path(self.pos_info['file_path'])
            })
        constants.UPLOAD_INFO['asset'] = self.upload_info["asset"]
        utils.json_save(self.upload_json, constants.UPLOAD_INFO)

    def get_file_md5(self, file_path):
        """Generate the md5 values for the scenario."""
        hash_md5 = hashlib.md5()
        if os.path.exists(file_path):
            with open(file_path, 'rb') as file_path_f:
                while True:
                    data_flow = file_path_f.read(8096)
                    if not data_flow:
                        break
                    hash_md5.update(data_flow)
        return hash_md5.hexdigest()

    def get_file_base64(self, file_path):
        """Generate the base64 values for the kml."""
        base64_str = ""
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file_path_f:
                data_flow = file_path_f.read()
                print(data_flow)
                base64_str = data_flow.encode("utf-8")
        return base64.b64encode(base64_str).decode("utf-8")

    def analyse_xml_file(self, xml_file):
        """  Check is the xml file and TiePoints in it."""
        tree = ET.parse(xml_file)
        root = tree.getroot()
        tie_points = root.find('Block').find('TiePoints')
        return True if tie_points else False

    def check_result(self):
        """Check that the analysis results file exists."""
        for json_path in [self.task_json, self.asset_json,
                          self.upload_json]:
            if not os.path.exists(json_path):
                msg = "Json file is not generated: {0}".format(json_path)
                return False, msg
        return True, None

    def analyse(self):
        """
            generate an upload json file.
        """

        self.write_task_json()
        self.write_upload_json()
        self.write_asset_json()

        status, msg = self.check_result()
        if status is False:
            self.add_tip(tips_code.UNKNOW_ERR, msg)
            self.save_tips()
            raise AnalyseFailError(msg)
