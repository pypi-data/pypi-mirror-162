# encoding: utf-8
"""
@project: djangoModel->equipment_map
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 设备映射
@created_time: 2022/8/9 11:43
"""
from django.core.paginator import Paginator
from rest_framework.views import APIView

from xj_equipment.models import EquipmentUseToMap, EquipmentUse, Equipment
from xj_equipment.utils.model_handle import util_response, parse_model, parse_data


class EquipmentUseMap(APIView):
    def get(self, request):
        params = request.query_params.copy()
        size = params.get('size', 20)
        page = params.get('page', 1)
        from_data = parse_data(request, [
            'use_id',
            'equip_id',
        ])
        list_set = EquipmentUseToMap.objects.filter(**from_data)
        count = list_set.count()
        limit_set = Paginator(list_set, size)
        page_set = limit_set.get_page(page)
        return util_response(data={'count': count, "page": page, "size": size, "list": parse_model(page_set)})

    def post(self, request):
        use_id = request.POST.get('use_id', None)
        equip_id = request.POST.get('equip_id', None)
        if not use_id or not equip_id:
            # 参数错误
            return util_response(err=45648, msg="参数错误")
        use_id_is_set = parse_model(EquipmentUse.objects.filter(id=use_id))
        equip_id_is_set = parse_model(Equipment.objects.filter(id=equip_id))
        if not use_id_is_set or not equip_id_is_set:
            return util_response(err=45648, msg="用途ID或者设备ID不存在")

        res = parse_model(EquipmentUseToMap.objects.filter(use_id=use_id, equip_id=equip_id))
        if not res:
            EquipmentUseToMap.objects.create(use_id=use_id, equip_id=equip_id)
            return util_response(msg="绑定成功")
        else:
            return util_response(msg="已经绑定过了,请勿重复操作")

    def delete(self, request):
        id = request.data.get("id", None)
        if id is None:
            return util_response(err=78965, msg='参数错误')
        res = EquipmentUseToMap.objects.get(id=id)
        if not res:
            return util_response(err=87878, msg="参数错误")
        res.delete()
        return util_response()
