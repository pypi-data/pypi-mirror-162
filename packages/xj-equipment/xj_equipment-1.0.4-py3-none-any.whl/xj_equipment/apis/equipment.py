# encoding: utf-8
"""
@project: djangoModel->equipment
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 设备相关接口
@created_time: 2022/8/5 11:01
"""

# =============设备===================
from rest_framework.views import APIView

from xj_equipment.customValidator import CreatedValidate
from xj_equipment.services.equipment_service import EquipmentService
from ..models import Equipment, EquipmentUseToMap, EquipmentUse
from ..utils.model_handle import parse_data, model_select, model_delete, JsonResponse, parse_model, util_response


class CreatedEquipment(APIView):
    # 添加设备
    def post(self, request):
        from_data = parse_data(request, [
            'equip_code',
            'region_code',
            'longitude',
            'latitude',
            'address',
            'equip_type',
            'name',
            'equip_type_id',
            'url',
            'mac',
            'description',
            'warning_toplimit',
            'setup_time',
            'admin_id'
        ])
        validator = CreatedValidate(from_data)
        validate_res, validate_error = validator.validate()
        if not validate_res:
            return util_response(err=5778, msg=validate_error)
        data, err = EquipmentService.add_equipment(from_data)
        if not err:
            return util_response()
        return util_response(err=5778, msg=err)


class DelEquipment(APIView):
    # 删除设备
    def post(self, request):
        from_data = parse_data(request)
        res = Equipment.objects.filter(id=from_data['id'])
        if not res:
            return util_response(err=7557, msg="数据已不存在")
        res.delete()
        return util_response()


class EquipmentList(APIView):
    # 设备列表
    def get(self, request):
        from_data = parse_data(request)
        data, err = EquipmentService.equipment_list(params=from_data)
        if not err:
            return util_response(data=data)
        return util_response(err=5779, msg=err)


class EquipmentUpdate(APIView):
    # 设备更新
    def post(self, request):
        if not request.data.get('id', None):
            return util_response(err=5577, msg='参数错误')
        from_data = parse_data(request, [
            'id',
            'equip_code',
            'region_code',
            'longitude',
            'latitude',
            'address',
            'equip_type',
            'name',
            'mac',
            'description',
            'warning_toplimit',
            'setup_time',
            'admin_id'
        ])
        data, err = EquipmentService.edit_equipment(from_data)
        if not err:
            return util_response()
        return util_response(err=5778, msg=err)




