# -*- coding: utf-8 -*-
from dayan_api.core import RayvisionAPI
from dayan_contextcapture.analyze_contextcapture import AnalyzeContextCapture
from dayan_sync.upload import RayvisionUpload
from dayan_sync.download import RayvisionDownload
from dayan_api.task.check import RayvisionCheck
from dayan_api.utils import update_task_info

# 区块提交重建、生产、自动下载成果

# API Parameter
render_para = {
    "domain": "task.dayancloud.com",
    "platform": "54",
    "access_id": "MlIdfMVJxTjUraMgklfd4hwpnCrm3rLN",
    "access_key": "f3a361d7f4d2dfc95b6c8a469dbc08d9",
}

api = RayvisionAPI(access_id=render_para['access_id'],
                   access_key=render_para['access_key'],
                   domain=render_para['domain'],
                   platform=render_para['platform'])
print(api.user_info)

"""
cg_file: （必填）上传照片资源的路径
xml_file：（选填）区块文件路径，不填为提交空三，填了走区块重建
world_coord_sys：（必填）坐标系
output_type：（必填）生产类型
kml_file：（选填）范围文件
photo_group_path：（必填）照片资源路径
workspace：（必填）本地配置文件存放区
project_name：（必填）工程名
platform：平台代号，24为测试，54为线上
sensor_size：（选填）传感器尺寸
tile_mode：瓦片切块方式，0为规则水平切块，1为自适应切块（默认为0）
is_set_origin_coord:是否自定义瓦片偏移，1为是，默认0
origin_coord:（选填）瓦片偏移
is_set_offset_coord: 是否自定义生产坐标原点，1为是，默认0
offsetCoord:（选填）生产坐标原点
"""
analyze_info = {
    "cg_file": r"G:\workspace",
    "xml_file": r"G:\luotuohe\Block_6 - AT - export.xml",
    "world_coord_sys": "EPSG:4546",
    "output_type": ["OSGB"],
    "kml_file": r"G:\luotuohe\fanwei.kml",
    "photo_group_path": [r"G:\luotuohe\Images"],
    "workspace": "G:/workspace1",
    "project_name": "SDK_TEST_rebuild_0718",
    "platform": render_para['platform'],
    "sensor_size": "",
    "tile_mode": "0",
    "is_set_origin_coord": "0",
    "origin_coord": {
        "coord_z": "",
        "coord_y": "",
        "coord_x": ""
    },
    "is_set_offset_coord": "0",
    "offset_coord": {
        "coord_z": "",
        "coord_y": "",
        "coord_x": ""
    }
}

# 生成配置文件
analyze_obj = AnalyzeContextCapture(**analyze_info)
analyze_obj.analyse()

# 设置配置信息
hardware_config = {}

# 检查配置文件
check_obj = RayvisionCheck(api, analyze_obj)
task_id = check_obj.execute(hardware_config, analyze_obj.task_json, analyze_obj.upload_json)
print('task_id', task_id)

# 更新task_id
update_task = {
    "task_id": task_id,
}
update_task_info(update_task, analyze_obj.task_json)

# 上传配置文件
CONFIG_PATH = {
    "tips_json_path": analyze_obj.tips_json,
    "task_json_path": analyze_obj.task_json,
    "asset_json_path": analyze_obj.asset_json,
    "upload_json_path": analyze_obj.upload_json
}
upload_obj = RayvisionUpload(api, automatic_line=True)

upload_method = 1
if upload_method == 1:
    upload_obj.upload(str(task_id), **CONFIG_PATH)

# 提交作业
api.submit_cc(int(task_id))

# 下载成果
download = RayvisionDownload(api)
# 任务所有帧渲染完成才开始下载，local_path为本地存放成果的路径
download.auto_download_cc_after_task_completed([int(task_id)], download_filename_format="false",
                                               local_path=r"G:\sdk_result\rebuild", download_type='render')
