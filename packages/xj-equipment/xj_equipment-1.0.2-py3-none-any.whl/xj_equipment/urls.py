# encoding: utf-8
"""
@project: djangoModel->urls
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 子路由文件
@created_time: 2022/6/7 13:53
"""
from django.urls import path, re_path

from .apis.equipment import CreatedEquipment, DelEquipment, EquipmentList, EquipmentUpdate, EquipmentUseMap  # 设备创建
from .apis.equipment_configure import GetEquipment  # 设备相关信息获取
from .apis.equipment_warning import EquipmentWarningReport  # 设备 应急预警（包括人工上报系统）
from .apis.equopment_record import AddEquipmentLog, UpdateEquipmentLog, EquipmentLogList  # 日志

urlpatterns = [
    # 设备管理
    path('create/', CreatedEquipment.as_view()),  # 创建/注册设备
    path('del/', DelEquipment.as_view()),  # 创建/注册设备
    path('list/', EquipmentList.as_view()),  # 设备列表
    path('update/', EquipmentUpdate.as_view()),  # 设备列表
    path('get_equipment_type/', GetEquipment.get_equipment_type),  # 设备类型
    path('use_map/', EquipmentUseMap.as_view()),  # 获取用途映射 CURD

    # 获取设备相关信息
    path('get_use_type/', GetEquipment.get_use_type),  # 获取使用类型
    path('get_equipment_flag/', GetEquipment.get_equipment_flag),  # 获取计量类型
    path('get_equipment_uint/<flag_id>', GetEquipment.get_equipment_uint),  # 获取计量单位
    path('get_equipment_uint/', GetEquipment.get_equipment_uint),  # 获取计量单位

    # 设备记录管理
    re_path('^record[/|_]create/?$', AddEquipmentLog.as_view()),  # 创建/注册设备ok
    re_path('^record[/|_]update/?$', UpdateEquipmentLog.as_view()),  # 创建/注册设备
    re_path('^record[/|_]list/?$', EquipmentLogList.as_view()),  # 创建/注册设备
    re_path('^record[/|_]statistics/?$', EquipmentLogList.statistics),  # 创建/注册设备

    # 设备记录上报
    path('warning/', EquipmentWarningReport.as_view()),  # 创建/注册设备ok
]
