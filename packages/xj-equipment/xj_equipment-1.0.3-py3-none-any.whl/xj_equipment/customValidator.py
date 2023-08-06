# encoding: utf-8
"""
@project: djangoModel->customValidator
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 用户自定义验证器
@created_time: 2022/8/5 10:57
"""
import json

from django import forms
from rest_framework.exceptions import ValidationError

from .models import Equipment, EquipmentFlag, EquipmentUint
from .utils.model_handle import parse_model


class Validate(forms.Form):
    """检验基类，子类编写规则，调用父类的validate方法"""

    def validate(self):
        """
        request 请求参数验证
        :return {'code': 'err': self.errors}:
        """
        if self.is_valid():
            return True, None
        else:
            error = json.dumps(self.errors)
            error = json.loads(error)
            temp_error = {}
            # 统一展示小写 提示，中文转义回来
            for k, v in error.items():
                temp_error[k.lower()] = v[0]
            return False, temp_error


class CreatedValidate(Validate):
    """验证查询表单"""
    equip_code = forms.CharField(
        required=True,
        error_messages={
            "required": "设备编码 必填",
        })
    equip_type_id = forms.IntegerField(
        required=True,
        error_messages={
            "required": "设备类型 必填",
        })

    address = forms.CharField(
        required=True,
        error_messages={
            "required": "设备物理地址 必填",
        })
    name = forms.CharField(
        required=True,
        error_messages={
            "required": "设备名称 必填",
        })
    url = forms.CharField(
        required=True,
        error_messages={
            "required": "设备路由 必填",
        })
    mac = forms.CharField(
        required=True,
        error_messages={
            "required": "设备IP 必填",
        })

    longitude = forms.CharField(
        required=True,
        error_messages={
            "required": "定位 必填",
        })
    latitude = forms.CharField(
        required=True,
        error_messages={
            "required": "定位 必填",
        })


# ====================== 记录验证 ====================
def log_equip_id(value):
    res = parse_model(Equipment.objects.filter(id=value))
    if not res:
        raise ValidationError('该设备ID不存在')


def log_flag_id(value):
    res = parse_model(EquipmentFlag.objects.filter(id=value))
    if not res:
        raise ValidationError('Flag_id不存在')


def log_unit_id(value):
    res = parse_model(EquipmentUint.objects.filter(id=value))
    if not res:
        raise ValidationError('unit_id不存在')


class RecordValidator(Validate):
    equip_id = forms.IntegerField(
        required=True,
        validators=[log_equip_id],
        error_messages={
            "required": "equip_id 必填",
        }
    )
    flag_id = forms.IntegerField(
        required=True,
        validators=[log_flag_id],
        error_messages={
            "required": "flag_id 必填",
        }
    )
    unit_id = forms.IntegerField(
        required=True,
        validators=[log_unit_id],
        error_messages={
            "required": "unit_id 必填",
        }
    )
    value = forms.IntegerField(
        required=True,
        error_messages={
            "required": "value 必填",
        }
    )


# ====================== 记录验证 end ====================


class WarnValidater(Validate):
    # equip = forms.IntegerField()
    # equip_record = forms.IntegerField()
    summary = forms.CharField(
        required=True,
        error_messages={
            "required": "summary 必填",
        }
    )
    work_level = forms.CharField(
        required=True,
        error_messages={
            "required": "work_level 必填",
        }
    )


class RecordWarnValidator(Validate):
    equip_id = forms.IntegerField(
        required=True,
        error_messages={
            "required": "equip_id 必填",
        }
    )
    equip_record_id = forms.IntegerField(
        required=True,
        error_messages={
            "required": "equip_record_id 必填",
        }
    )
    summary = forms.CharField(
        required=True,
        error_messages={
            "required": "summary 必填",
        }
    )
    work_level = forms.CharField(
        required=True,
        error_messages={
            "required": "work_level 必填",
        }
    )
