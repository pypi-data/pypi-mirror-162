from django.contrib import admin

from .models import Equipment, EquipmentRecord, EquipmentFlag, EquipmentUint, EquipmentUse, EquipmentUseToMap, \
    EquipmentType, equipmentWarn, EquipmentAttribute


class EquipmentManager(admin.ModelAdmin):
    list_display = ['id', 'name', 'address', 'equip_code', 'region_code', 'equip_type']
    list_editable = ['name', 'address', 'equip_code']
    search_fields = ['equip_code']
    list_filter = ['equip_type_id']
    fields = ('name', 'address', 'equip_code', 'region_code', 'equip_type', 'longitude', 'latitude')


class EquipmentAttributeManager(admin.ModelAdmin):
    list_display = ['id', 'name']
    fields = ['name']


class EquipmentRecordManager(admin.ModelAdmin):
    list_display = ['equip', 'summary', 'flag', 'unit', 'created_time', 'value']
    fields = ['equip', 'summary', 'flag', 'unit', 'created_time', 'value']
    search_fields = ['equip', 'flag', 'unit']


class EquipmentFlagManager(admin.ModelAdmin):
    list_display = ['id', 'flag']
    search_fields = ['id', 'flag']


class EquipmentUintManager(admin.ModelAdmin):
    list_display = ['id', 'flag', 'uint']
    list_filter = ['flag']


class EquipmentUseManager(admin.ModelAdmin):
    list_display = ['id', 'title', 'desc']
    list_editable = ['title', 'desc']
    search_fields = ['id', 'title', 'desc']


class EquipmentUseToMapManager(admin.ModelAdmin):
    list_display = ['id', 'equip', 'use']
    list_filter = ['use_id']


class EquipmentTypeManager(admin.ModelAdmin):
    list_display = ['id', 'equip_type']
    search_fields = ['id', 'equip_type']


class equipmentWarnManager(admin.ModelAdmin):
    list_display = ['id', 'equip', 'equip_record', 'summary', 'get_warning_level']
    search_fields = ['id', 'equip', 'equip_record', 'summary', 'get_warning_level']
    fields = ['equip', 'equip_record', 'summary', 'work_level']


admin.site.register(Equipment, EquipmentManager)
admin.site.register(EquipmentRecord, EquipmentRecordManager)
admin.site.register(EquipmentFlag, EquipmentFlagManager)
admin.site.register(EquipmentUint, EquipmentUintManager)
admin.site.register(EquipmentUse, EquipmentUseManager)
admin.site.register(EquipmentUseToMap, EquipmentUseToMapManager)
admin.site.register(EquipmentType, EquipmentTypeManager)
admin.site.register(equipmentWarn, equipmentWarnManager)
admin.site.register(EquipmentAttribute, EquipmentAttributeManager)
admin.site.site_header = 'msa一体化管理后台'
admin.site.site_title = 'msa一体化管理后台'
