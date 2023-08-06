# encoding: utf-8
"""
@project: djangoModel->service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 设备服务封装
@created_time: 2022/6/7 11:55
"""
from django.core.paginator import Paginator
from rest_framework import serializers

from xj_equipment.utils.model_handle import only_filed_handle, parse_model
from ..models import Equipment, EquipmentRecord


class EquipmentRecordSerializer(serializers.ModelSerializer):
    """展示类型序列化器"""

    class Meta:
        model = EquipmentRecord
        fields = [
            'sum_value',
            'hour'
        ]


# ============  设备服务类 start ==============
class EquipmentService():
    @staticmethod
    def add_equipment(params):
        # 添加设备
        try:
            Equipment.objects.create(**params)
        except Exception as e:
            return None, str(e)
        return None, None

    @staticmethod
    def edit_equipment(params):
        # 添加设备
        try:
            res = Equipment.objects.filter(id=params['id'])
            if not res:
                return None, "不存在ID位" + params['id'] + "该设备"
            res.update(**params)
        except Exception as e:
            return None, str(e)
        return None, None

    @staticmethod
    def equipment_list(params):
        page = params.pop('page', 1)
        size = params.pop('size', 20)
        params = only_filed_handle(params, {
            'equip_code': "equip_code",
            'region_code': "region_code",
            'longitude': "longitude",
            'latitude': "latitude",
            'address': "address__contains",
            'equip_type': 'equip_type',
            'name': "name__contains",
            'mac': "mac",
            'description': "description__contains",
            'warning_toplimit': "warning_toplimit",
            'setup_time': "setup_time",
            'id': "id",
        }, None)
        list_set = Equipment.objects.filter(**params)
        count = list_set.count()
        page_set = parse_model(Paginator(list_set, size).get_page(page))
        return {'count': count, "page": page, "size": size, "list": page_set}, 0
