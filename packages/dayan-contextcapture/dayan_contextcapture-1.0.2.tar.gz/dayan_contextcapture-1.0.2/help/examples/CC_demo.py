# -*- coding: utf-8 -*-
from dayan_api.core import RayvisionAPI
from dayan_contextcapture.analyze_contextcapture import AnalyzeContextCapture
from dayan_sync.upload import RayvisionUpload
from dayan_sync.download import RayvisionDownload
from dayan_api.task.check import RayvisionCheck
from dayan_api.utils import update_task_info
import os

# 提交空三后，自动重建生产、下载成果

# pos字段顺序
FIELD_ORDER = {
    "xyz": "name|X|Y|Z",
    "yxz": "name|Y|X|Z",
    "longitude_latitude": "name|longitude|latitude|altitude",
    "latitude_longitude": "name|latitude|longitude|altitude"

}

# pos文件分隔符
SPLIT_CHAR = {
    "point": ".",
    "tab": "\t",
    "space": " ",
    "comma": ",",
    "semicolon": ";"
}

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
is_submit_pos:是否提交pos文件(1为是，0为否) - 默认为0
pos_info：is_submit_pos为1时，此项必填
         field_order：字段顺序
         file_path：文件本地路径
         ignore_lines：忽略行数
         splite_char：分隔符
         coord_system：坐标系
pos_scope：如果上传pos文件，此项为必填
           is_all：是否应用于全部照片组，1为是，0为否
           scope: is_all为0时必填，填应用的照片组路径
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
is_many_at：是否分块空三，1为是，0为否;(默认0)
many_at：is_many_at为1时必填，file_path为kml文件路径，block_merge为1时分块合并，0表示分块不合并
"""
analyze_info = {
    "cg_file": r"G:\cg_file",
    "xml_file": r"",
    "is_submit_pos": "1",
    "pos_info": {
        "field_order": FIELD_ORDER["longitude_latitude"],
        "file_path": r"G:\test2（37）\11.txt",
        "ignore_lines": "1",
        "splite_char": SPLIT_CHAR['point'],
        "coord_system": "EPSG:32645"
    },
    "pos_scope": {
        "is_all": "1",
        "scope": []
    },
    "world_coord_sys": "EPSG:32645",
    "output_type": ["OSGB", "TIFF"],
    "kml_file": r"",
    "photo_group_path": [r"G:\test2（37）\Images"],
    "workspace": "G:/workspace",
    "project_name": "SDK_TEST_0718",
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
    },
    "is_many_at": "1",
    "many_at": {
        "kmls": [
            {"file_path": r"G:\luotuohe\fanwei.kml"},
            {"file_path": r"G:\luotuohe\fanwei1.kml"}
        ],
        "block_merge": 1
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

download = RayvisionDownload(api)
if not analyze_info['xml_file']:
    # 存放区块文件的本地地址
    local_path = r'G:\sdk_result\at'
    # 下载区块
    rebuild_exe = download.download_block(task_id_list=[int(task_id)], local_path=local_path, download_type='block')
    print('rebuild_exe', rebuild_exe)

    if rebuild_exe is True:
        # 重建准备
        analyze_info['xml_file'] = os.path.join(local_path, 'at_result/block.xml')

        query_task_rep = api.query.task_info(task_ids_list=[task_id])
        small_task_id = query_task_rep['items'][0]['respRenderingTaskList'][1]['id']
        print('small_task_id', small_task_id)
        # 提交重建
        api.submit_cc(int(small_task_id), option='rebuild',
                      param={'outputType': analyze_info['output_type'],
                             'worldCoordSys': analyze_info['world_coord_sys']})

        # 下载成果（任务所有帧渲染完成才开始下载）
        download.auto_download_cc_after_task_completed([int(task_id)], download_filename_format="false",
                                                       local_path=r"G:\sdk_result", download_type='render')

# 其他操作：重提&停止
# 查询子任务id
# query_task_rep = api.query.task_info(task_ids_list=[task_id])
# small_task_id = query_task_rep['items'][0]['respRenderingTaskList'][0]['id']
# print('small_task_id', small_task_id)

# 重提
"""
状态码：
1 等待
2 开始
3 中止
4 完成
5 失败
11 超时
"""

# task_param_list放任务id（small_task_id）
# api.query.restart_failed_frames(task_param_list=[24223893], status=[1, 2, 3, 4, 5, 11])

# 停止
# task_param_list放任务id（small_task_id）
# stop_task = api.task.stop_task(task_param_list=[24223901])
