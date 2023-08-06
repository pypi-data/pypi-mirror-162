# encoding: utf-8
"""
@project: djangoModel->record_warning_service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 预警模块
@created_time: 2022/8/8 18:12
"""
from django.core.paginator import Paginator

from xj_equipment.customValidator import RecordWarnValidator
from xj_equipment.models import equipmentWarn
from xj_equipment.utils.model_handle import only_filed_handle, parse_model


class EquipmentWarningService:
    @staticmethod
    def report(params):
        print("params:", params)
        validator = RecordWarnValidator(params)
        is_pass, err = validator.validate()
        if not is_pass:
            return None, err
        equipmentWarn.objects.create(**params)
        return None, None

    @staticmethod
    def list(params):
        validator = RecordWarnValidator(params)
        is_pass, err = validator.validate()
        if is_pass:
            return None, err
        page = params.pop('page', 1)
        size = params.pop('size', 20)
        params = only_filed_handle(params, {
            "equip_id": "equip_id",
            "equip_record_id": "equip_record_id",
            "summary": "summary__contains",
            "work_level": "work_level__contains"
        }, None)

        list_set = equipmentWarn.objects.filter(**params)
        count = list_set.count()
        limit_set = Paginator(list_set, size)
        page_set = limit_set.get_page(page)
        res = {'count': count, "page": page, "size": size, "list": parse_model(page_set)}
        return res, None
