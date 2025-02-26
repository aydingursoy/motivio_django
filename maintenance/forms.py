from django import forms
from .models import MaintenanceRecord, MaintenanceReminder
from decimal import Decimal

class MaintenanceRecordForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = ['category', 'service_date', 'mileage_at_service', 'service_provider',
                  'service_details', 'cost', 'receipt_image', 'notes']
        widgets = {
            'service_date': forms.DateInput(attrs={'type': 'date'}),
            'mileage_at_service': forms.NumberInput(attrs={'min': 0}),
            'cost': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        self.vehicle = kwargs.pop('vehicle', None)
        super(MaintenanceRecordForm, self).__init__(*args, **kwargs)

        # If there's a suggested cost, show it
        if 'category' in self.data:
            from .models import CostEstimate
            try:
                vehicle = self.vehicle
                category_id = int(self.data.get('category'))

                estimates = CostEstimate.objects.filter(
                    category_id=category_id,
                    make__iexact=vehicle.make,
                    year_start__lte=vehicle.year,
                    year_end__gte=vehicle.year
                )

                if estimates.exists():
                    estimate = estimates.first()
                    self.fields['cost'].help_text = (
                        f"Suggested cost range: ${estimate.min_cost} - ${estimate.max_cost} "
                        f"(Average: ${estimate.average_cost})"
                    )
                    self.estimated_cost = estimate.average_cost

            except (ValueError, TypeError):
                pass

class MaintenanceReminderForm(forms.ModelForm):
    class Meta:
        model = MaintenanceReminder
        fields = ['category', 'due_date', 'due_mileage', 'notes']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'due_mileage': forms.NumberInput(attrs={'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        self.vehicle = kwargs.pop('vehicle', None)
        super(MaintenanceReminderForm, self).__init__(*args, **kwargs)

        if self.vehicle:
            # Set initial due mileage based on current mileage and suggested interval
            self.fields['due_mileage'].initial = self.vehicle.current_mileage

        # When category changes, update due mileage based on suggested interval
        if 'category' in self.data:
            from .models import MaintenanceCategory
            try:
                category_id = int(self.data.get('category'))
                category = MaintenanceCategory.objects.get(id=category_id)

                if category.suggested_interval_miles and self.vehicle:
                    self.fields['due_mileage'].initial = self.vehicle.current_mileage + category.suggested_interval_miles

            except (ValueError, TypeError, MaintenanceCategory.DoesNotExist):
                pass
