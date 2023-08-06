# encoding: utf-8
"""
@project: djangoModel->equopment_log
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 日志API
@created_time: 2022/8/5 11:13
"""
import datetime

from rest_framework.views import APIView

from xj_equipment.customValidator import RecordValidator
from ..models import Equipment
from ..services.equipment_record_service import EquipmentRecordService
from ..utils.model_handle import parse_data, util_response, parse_model


class AddEquipmentRecord(APIView):
    # 添加设备记录
    def post(self, request):
        form_data = parse_data(request)

        # 补全equip_id
        equip_code = form_data.pop("equip_code", None)
        if not form_data.get("equip_id", None):
            if equip_code is None:
                return util_response(err=2548, msg="未找到该设备")
            equip_obj = parse_model(Equipment.objects.filter(equip_code=equip_code))
            if not equip_obj:
                return util_response(err=2548, msg="未找到该设备")
            form_data['equip_id'] = equip_obj[0]['id']

        # 数据有效新判断
        validator = RecordValidator(form_data)
        is_pass, msg = validator.validate()
        if not is_pass:
            return util_response(err=54548, msg=msg)

        # 插入数据
        data, err_txt = EquipmentRecordService.add_record(form_data)
        if not err_txt:
            return util_response()
        return util_response(err=55796, msg=err_txt)


class EditEquipmentRecord(APIView):
    # 设备状态更新
    def post(self, request):
        form_data = parse_data(request)
        data, err_txt = EquipmentRecordService.edit_record(form_data)
        if not err_txt:
            return util_response()
        return util_response(err=55796, msg=err_txt)


class EquipmentRecordList(APIView):
    # 添加/修改日志
    def get(self, request):
        data, err_txt = EquipmentRecordService.record_list(request.query_params.copy())
        if not err_txt:
            return util_response(data=data)
        return util_response(err=55796, msg=err_txt)


class EquipmentRecordStatistic(APIView):
    # 记录分组展示
    def statistics(self):
        form_data = parse_data(self)
        date = form_data.pop('date', None)
        if date is None:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
        else:
            today = date
        form_data['created_time__gte'] = today + " 09:00:00"
        form_data['created_time__lte'] = today + " 22:00:00"
        data, err_txt = EquipmentRecordService.record_statistics(form_data)
        if not err_txt:
            return util_response(data=data)
        return util_response(err=55796, msg=err_txt)
