from rest_framework import serializers
from vehicles.models import Vehicle, MileageRecord
from maintenance.models import MaintenanceRecord, MaintenanceReminder, CostEstimate, MaintenanceCategory

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'nickname', 'make', 'model', 'year', 'vin', 'license_plate',
                 'current_mileage', 'image', 'date_added']
        read_only_fields = ['date_added']

class MileageRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MileageRecord
        fields = ['id', 'vehicle', 'mileage', 'date_recorded', 'notes']

class MaintenanceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceCategory
        fields = ['id', 'name', 'description', 'suggested_interval_miles', 'suggested_interval_months']

class MaintenanceRecordSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    vehicle_info = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceRecord
        fields = ['id', 'vehicle', 'vehicle_info', 'category', 'category_name', 'service_date',
                  'mileage_at_service', 'service_provider', 'service_details', 'cost',
                  'estimated_cost', 'receipt_image', 'notes', 'date_created']
        read_only_fields = ['date_created']

    def get_vehicle_info(self, obj):
        return f"{obj.vehicle.year} {obj.vehicle.make} {obj.vehicle.model}"

class MaintenanceReminderSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    vehicle_info = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceReminder
        fields = ['id', 'vehicle', 'vehicle_info', 'category', 'category_name', 'due_date',
                  'due_mileage', 'status', 'notes', 'last_service_date',
                  'last_service_mileage', 'suggested_cost']

    def get_vehicle_info(self, obj):
        return f"{obj.vehicle.year} {obj.vehicle.make} {obj.vehicle.model}"

class CostEstimateSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = CostEstimate
        fields = ['id', 'category', 'category_name', 'make', 'model', 'year_start',
                  'year_end', 'min_cost', 'max_cost', 'average_cost']
