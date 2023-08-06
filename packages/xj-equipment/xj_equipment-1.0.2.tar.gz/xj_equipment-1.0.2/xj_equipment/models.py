import time

from django.db import models
from django.utils import timezone

from .config import equipment_warning_level


class EquipmentType(models.Model):
    id = models.IntegerField(primary_key=True, null=False, auto_created=True)
    equip_type = models.CharField('用途ID', null=False, default=0, max_length=50)

    class Meta:
        managed = False
        db_table = "equipment_type"
        verbose_name = "2.设备类型表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.equip_type


class Equipment(models.Model):
    id = models.IntegerField(primary_key=True, null=False, auto_created=True)
    equip_code = models.CharField('设备编码', max_length=100, null=False, default="")
    region_code = models.CharField('行政编码', max_length=100, null=False, default="")
    longitude = models.CharField('经度', null=False, default="", max_length=25)
    latitude = models.CharField('维度', null=False, default="", max_length=25)
    address = models.CharField('详细地址', null=False, default="", max_length=255)
    admin_id = models.IntegerField('是否删除', null=False, default=0)
    # equip_type_id = models.IntegerField('设备类型', null=False, default=0)
    equip_type = models.ForeignKey('EquipmentType', null=True, blank=True, on_delete=models.CASCADE,
                                   verbose_name='设备类型')
    name = models.CharField('名称', null=False, default="", max_length=255)
    url = models.CharField('路由', null=False, default="", max_length=255)
    mac = models.CharField('设备IP地址', null=False, default="", max_length=255)
    status = models.IntegerField('设备状态', null=False, default=0)
    detail_json = models.JSONField('扩展配置', default=dict, null=False, blank=True)
    description = models.CharField('设备描述', null=False, default="", max_length=255)
    setup_time = models.DateTimeField('创建时间', null=False,
                                      default=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    updated_time = models.DateTimeField('更新时间', null=False, auto_now=True)
    warning_toplimit = models.IntegerField('告警上线', null=False, blank=True, default=0)

    class Meta:
        managed = False
        db_table = "equipment_equipment"
        verbose_name = "1.设备表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class EquipmentAttribute(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('属性名称', null=False, default="", max_length=255)

    class Meta:
        managed = False
        db_table = "equipment_attribute"
        verbose_name_plural = "9.属性扩展表"

    def __str__(self):
        return self.name if self.name else ""


class EquipmentRecord(models.Model):
    id = models.AutoField(primary_key=True)
    equip = models.ForeignKey('Equipment', null=True, blank=True, on_delete=models.CASCADE, verbose_name='设备')
    flag = models.ForeignKey('EquipmentFlag', null=True, blank=True, on_delete=models.CASCADE, verbose_name='计量标志类型')
    unit = models.ForeignKey('EquipmentUint', null=True, blank=True, on_delete=models.CASCADE, verbose_name='计量标志单位')
    value = models.DecimalField('单位值', null=False, max_digits=11, decimal_places=2, default=0)
    status = models.IntegerField('设备状态', null=False, default=0)
    summary = models.CharField('记录摘要', null=False, default="", max_length=255)
    created_time = models.DateTimeField('创建时间', null=True, blank=True, default=timezone.now)
    updated_time = models.DateTimeField('更新时间', null=False, auto_now=True)
    attribute = models.ForeignKey("EquipmentAttribute", verbose_name='属性id', on_delete=models.CASCADE, )
    hour = models.Aggregate()

    class Meta:
        managed = False
        db_table = "equipment_record"
        verbose_name = "7.记录表"
        verbose_name_plural = verbose_name

    # def __str__(self):
    #     return self.summary


class EquipmentFlag(models.Model):
    id = models.IntegerField(primary_key=True, null=False, auto_created=True)
    flag = models.CharField('计量类型', null=False, default="", max_length=50)

    class Meta:
        managed = False
        db_table = "equipment_flag"
        verbose_name = "4.计量表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.flag


class EquipmentUint(models.Model):
    id = models.IntegerField(primary_key=True, null=False, auto_created=True)
    uint = models.CharField('单位', null=False, default="", max_length=50)
    # flag_id = models.IntegerField('计量类型ID', null=False, default="")
    flag = models.ForeignKey('EquipmentFlag', null=True, blank=True, on_delete=models.CASCADE, verbose_name='类别')

    class Meta:
        managed = False
        db_table = "equipment_unit"
        verbose_name = "3.单位表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.uint


class EquipmentUse(models.Model):
    id = models.IntegerField(primary_key=True, null=False, auto_created=True)
    title = models.CharField('用途', null=False, default="", max_length=255)
    desc = models.CharField('用途描述', null=False, default="", max_length=255)

    class Meta:
        managed = False
        db_table = "equipment_use"
        verbose_name = "5.用途类型表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class EquipmentUseToMap(models.Model):
    id = models.IntegerField(primary_key=True, null=False, auto_created=True)
    use = models.ForeignKey('EquipmentUse', null=True, blank=True, on_delete=models.CASCADE, related_name='用途',
                            verbose_name='用途')
    equip = models.ForeignKey('Equipment', null=True, blank=True, on_delete=models.CASCADE, related_name='设备',
                              verbose_name='设备')

    class Meta:
        managed = False
        db_table = "equipment_use_to_map"
        verbose_name = "6.用途映射表"
        verbose_name_plural = verbose_name


# 告警模块
class equipmentWarn(models.Model):
    id = models.IntegerField(primary_key=True, null=False, auto_created=True)
    equip = models.ForeignKey('Equipment', null=True, blank=True, on_delete=models.CASCADE, verbose_name='设备', )
    equip_record = models.ForeignKey('EquipmentRecord', null=True, blank=True, on_delete=models.CASCADE, verbose_name='异常记录', default=0)
    summary = models.CharField('告警原因/摘要', null=True, blank=True, default="", max_length=255)
    work_level = models.CharField('告警等级', null=True, blank=True, default="", max_length=255)

    class Meta:
        managed = False
        db_table = "equipment_warn"
        verbose_name_plural = "8.设备告警"

    def get_warning_level(self):
        if self.work_level in equipment_warning_level:
            return equipment_warning_level[self.work_level]
        else:
            return self.work_level
