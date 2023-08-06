# encoding: utf-8
"""
@project: djangoModel->record_service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 设备记录服务
@created_time: 2022/8/8 17:22
"""

# ===========  日志服务基类 start =============
from django.core.paginator import Paginator
from django.db.models import Sum
from django.db.models.functions import TruncHour

from xj_equipment.models import EquipmentRecord
from xj_equipment.utils.model_handle import only_filed_handle, parse_model


class EquipmentRecordService:
    @staticmethod
    def add_record(form_data):
        try:
            record = EquipmentRecord.objects.create(**form_data)
            res = {'id': record.id, 'equip_id': record.equip_id}
            return None, res
        except Exception as e:
            return None, str(e)

    @staticmethod
    def edit_record(form_data):
        try:
            id = form_data.pop('id')
            res = EquipmentRecord.objects.filter(id=id)
            res.update(**form_data)
            return None, None
        except Exception as e:
            return 5578, str(e)

    @staticmethod
    def record_list(form_data):
        only_filed_dict = {
            "start_time": "created_time_gte",
            "end_time": "created_time_lte",
            "equip_id": "equip_id",
            "status": "status",
            "summary": "summary__contains",
            "value": "value",
            "attribute_id": "attribute_id"
        }
        page = form_data.pop('page', 1)
        size = form_data.pop('size', 20)
        form_data = only_filed_handle(form_data, only_filed_dict, None)
        list_set = EquipmentRecord.objects.filter(**form_data)
        count = list_set.count()
        page_set = parse_model(Paginator(list_set, size).get_page(page))
        return {'count': count, "page": page, "size": size, "list": page_set}, 0

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
            print("res_set", res_set)
            return res_set, None
        except Exception as e:
            return None, str(e)
