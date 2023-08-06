# encoding: utf-8
"""
@project: djangoModel->config
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 设备配置文件按
@created_time: 2022/6/7 11:58
"""

equipment_type = {
    '监控': 0,
    "声控": 1,
    '温控': 2,
    '闸机': 3
}

# normal, warning, danger, error, damage, offline, trunoff

equipment_warning_level = {
    "normal": "普通",
    "warning": "告警",
    "danger": "危险",
    "offline": " 脱机",
    "trunoff": "断线"
}
