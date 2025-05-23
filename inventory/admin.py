from django.contrib import admin
from .models import DeviceType, Device,MaintenanceCheckpoint,MaintenanceRecord,Checkpoint

@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Checkpoint)
class CheckpointAdmin(admin.ModelAdmin):
    list_display = ( 'description',"is_checked",)
    search_fields = ('description',)

@admin.register(MaintenanceCheckpoint)
class MaintenanceCheckpointAdmin(admin.ModelAdmin):
    list_display = ( 'description',"is_checked",)
    search_fields = ('description',)


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'serial_number', 'device_type', 'status', 'acquisition_date')
    list_filter = ('device_type', 'status', 'acquisition_date')
    search_fields = ('name', 'serial_number', 'model')
    readonly_fields = ('barcode',)


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ('device', 'maintenance_date', 'maintenance_type', 'performed_by')
    list_filter = ('maintenance_date', 'maintenance_type')
    search_fields = ('device__name', 'device__serial_number', 'description')




