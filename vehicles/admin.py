from django.contrib import admin
from .models import Vehicle, MileageRecord

class MileageRecordInline(admin.TabularInline):
    model = MileageRecord
    extra = 0

class VehicleAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year', 'nickname', 'user', 'current_mileage', 'date_added')
    list_filter = ('make', 'year', 'user')
    search_fields = ('make', 'model', 'nickname', 'vin', 'license_plate')
    inlines = [MileageRecordInline]
    readonly_fields = ('date_added',)

admin.site.register(Vehicle, VehicleAdmin)

class MileageRecordAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'mileage', 'date_recorded')
    list_filter = ('date_recorded', 'vehicle__make', 'vehicle__model')
    search_fields = ('vehicle__make', 'vehicle__model', 'vehicle__nickname')

admin.site.register(MileageRecord, MileageRecordAdmin)
