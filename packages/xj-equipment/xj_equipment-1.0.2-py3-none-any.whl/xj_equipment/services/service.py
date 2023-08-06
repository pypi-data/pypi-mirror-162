# encoding: utf-8
"""
@project: djangoModel->service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 设备服务封装
@created_time: 2022/6/7 11:55
"""
from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncWeek, TruncYear, TruncDay, TruncHour
from django.forms.models import model_to_dict
from rest_framework import status, serializers

from ..customValidator import CreatedValidate, RecordValidator
from ..models import Equipment, EquipmentRecord
from ..utils.custom_response import util_response
from ..utils.model_handle import parse_model


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
    def add_equipment(self, params):
        # 添加设备
        try:
            validator = CreatedValidate(params)
            validate_res, validate_error = validator.validate()
            if validate_res:
                Equipment.objects.create(**params)
            else:
                return util_response('', 7557, status.HTTP_200_OK, validate_error)
        except Exception as e:
            return util_response('', 7557, status.HTTP_200_OK, str(e))
        return util_response('', 0, status.HTTP_200_OK, "ok")


# ===========  日志服务基类 start =============
class EquipmentRecordService:
    def add_record(self, form_data):
        try:
            validator = RecordValidator(form_data)
            is_pass, msg = validator.validate()
            if is_pass:
                record = EquipmentRecord.objects.create(**form_data)
                res = {'id': record.id, 'equip_id': record.equip_id}
                return util_response(res, 0, status.HTTP_200_OK, "ok")
            else:
                return util_response('', 7557, status.HTTP_200_OK, str(msg))
        except Exception as e:
            return util_response('', 7557, status.HTTP_200_OK, str(str(e)))

    def edit_record(self, form_data):
        try:
            id = form_data['id']
            del form_data['id']
            res = EquipmentRecord.objects.filter(id=id)
            res.update(**form_data)
            return util_response()
        except Exception as e:
            return util_response(err=5578, msg=str(e))

    def record_list(self, form_data):
        try:
            res = EquipmentRecord.objects.filter(**form_data)
            return util_response(parse_model(res), 0, status.HTTP_200_OK, "ok")
        except Exception as e:
            return util_response('', 7557, status.HTTP_200_OK, str(str(e)))

    @staticmethod
    def record_statistics(params):
        """
        场馆人流量统计
        原sql
        EquipmentRecord.objects.extra(select={"created_hour": 'date_format(created_time,"%%H")', }).filter(**params).values("created_hour").annotate(sum_value=Sum("value"))
        新sql
        EquipmentRecord.objects.filter(**params).annotate(created_hour=TruncHour("created_time")).values('created_hour').annotate(sum_value=Sum("value"))
        """
        try:
            params['attribute_id'] = 1
            input_sets = list(EquipmentRecord.objects.filter(**params).annotate(created_hour=TruncHour("created_time")).values('created_hour').annotate(sum_value=Sum("value")))
            params['attribute_id'] = 2
            output_sets = list(EquipmentRecord.objects.filter(**params).annotate(created_hour=TruncHour("created_time")).values('created_hour').annotate(sum_value=Sum("value")))
            # 格式化数据
            format_in = input_sets
            format_out = output_sets
            for index, item in enumerate(input_sets):
                format_in[index]['sum_value'] = int(item['sum_value'])
                format_in[index]['created_hour'] = int(item['created_hour'].strftime("%H"))
            for index, item in enumerate(format_out):
                format_out[index]['sum_value'] = int(item['sum_value'])
                format_out[index]['created_hour'] = int(item['created_hour'].strftime("%H"))
            res_set = {"in_visitors_flowrate": format_in, "out_visitors_flowrate": format_out}
            return util_response(data=res_set)
        except Exception as e:
            return util_response(err=5577, msg=str(e))
