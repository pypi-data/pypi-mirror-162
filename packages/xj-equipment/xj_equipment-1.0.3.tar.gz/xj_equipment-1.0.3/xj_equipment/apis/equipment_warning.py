# encoding: utf-8
"""
@project: djangoModel->equipment_warning
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 设备告警
@created_time: 2022/8/5 11:15
"""
from rest_framework.views import APIView

from xj_equipment.services.equipment_warning_service import EquipmentWarningService
from ..utils.model_handle import parse_data, util_response


class EquipmentWarningReport(APIView):
    # 手动上报接口
    def post(self, request):
        params = parse_data(request, [
            "equip_id",
            "equip_record_id",
            "summary",
            "work_level"
        ])
        data, err_txt = EquipmentWarningService.report(params)
        if not err_txt:
            return util_response()
        return util_response(err=55796, msg=err_txt)

    # 告警列表
    def get(self, request):
        params = parse_data(request, [
            "equip_id",
            "equip_record_id",
            "summary",
            "work_level",
            "page",
            "size"
        ])
        data, err_txt = EquipmentWarningService.list(params)
        if not err_txt:
            return util_response(data=data)
        return util_response(err=55796, msg=err_txt)
