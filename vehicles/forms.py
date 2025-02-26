from django import forms
from .models import Vehicle, MileageRecord

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['nickname', 'make', 'model', 'year', 'vin', 'license_plate', 'current_mileage', 'image']
        widgets = {
            'year': forms.NumberInput(attrs={'min': 1900, 'max': 2025}),
            'current_mileage': forms.NumberInput(attrs={'min': 0}),
        }

    def clean_vin(self):
        vin = self.cleaned_data.get('vin')
        if vin:
            # Basic VIN validation (17 characters for modern vehicles)
            if len(vin) != 17 and len(vin) > 0:
                raise forms.ValidationError("VIN should be 17 characters for modern vehicles.")
        return vin

class MileageRecordForm(forms.ModelForm):
    class Meta:
        model = MileageRecord
        fields = ['mileage', 'date_recorded', 'notes']
        widgets = {
            'date_recorded': forms.DateInput(attrs={'type': 'date'}),
            'mileage': forms.NumberInput(attrs={'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        self.vehicle = kwargs.pop('vehicle', None)
        super(MileageRecordForm, self).__init__(*args, **kwargs)

    def clean_mileage(self):
        mileage = self.cleaned_data.get('mileage')
        if self.vehicle and mileage < self.vehicle.current_mileage:
            raise forms.ValidationError("Mileage cannot be less than the current vehicle mileage.")
        return mileage
