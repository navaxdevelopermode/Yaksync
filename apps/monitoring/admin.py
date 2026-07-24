from django.contrib import admin
from .models import SensorReading


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ['device', 'animal', 'temperature', 'movement', 'is_abnormal', 'timestamp']
    list_filter = ['is_abnormal', 'timestamp']
    search_fields = ['device__device_id', 'device__name', 'animal__animal_id', 'animal__name']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'

