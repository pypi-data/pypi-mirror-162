# encoding: utf-8
"""
@project: djangoModel->equipment_configure
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 设备相关类型列表查询
@created_time: 2022/8/5 11:09
"""
from django.views.decorators.http import require_http_methods
from rest_framework.views import APIView

from ..models import EquipmentType, EquipmentUse, EquipmentFlag, EquipmentUint
from ..utils.custom_response import util_response
from ..utils.model_handle import parse_model


class GetEquipmentTypes(APIView):
    @require_http_methods(["GET"])
    def get_equipment_type(self):
        return util_response(parse_model(EquipmentType.objects.all()))

    @require_http_methods(["GET"])
    def get_use_type(self):
        return util_response(parse_model(EquipmentUse.objects.all()))

    @require_http_methods(["GET"])
    def get_equipment_flag_type(self):
        all_set = parse_model(EquipmentFlag.objects.all())
        return util_response(all_set)

    @require_http_methods(["GET"])
    def get_equipment_uint_type(self, flag_id=None):
        if not flag_id:
            all_set = parse_model(EquipmentUint.objects.all())
        else:
            all_set = parse_model(EquipmentUint.objects.filter(flag_id=flag_id))
        return util_response(all_set)
