from django.contrib import admin
from .models import Animal


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = [
        'animal_id', 'name', 'date_of_birth', 'age', 'parity', 
        'vagina_temperature', 'health_status', 'reproductive_status'
    ]
    list_filter = ['species', 'breed', 'health_status', 'reproductive_status', 'breeding_method']
    search_fields = ['animal_id', 'name', 'dam', 'sire', 'description']
    readonly_fields = ['age', 'registration_date', 'created_at', 'updated_at']
    fieldsets = (
        ('Identification & Specs', {
            'fields': ('animal_id', 'name', 'species', 'breed', 'description')
        }),
        ('Birth & Physical Attributes', {
            'fields': ('date_of_birth', 'age', 'weight')
        }),
        ('Reproductive Measurements', {
            'fields': (
                'vulva_length', 'vaginal_depth', 'distance_to_cervix', 
                'vaginal_diameter', 'parity', 'vagina_temperature'
            )
        }),
        ('Health & Breeding', {
            'fields': ('health_status', 'reproductive_status', 'dam', 'sire', 'breeding_method')
        }),
        ('Metadata', {
            'fields': ('created_by', 'registration_date', 'created_at', 'updated_at')
        }),
    )
