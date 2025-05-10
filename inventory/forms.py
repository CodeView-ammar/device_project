from django import forms
from .models import Device, DeviceType, MaintenanceRecord
from django.utils import timezone


class DeviceForm(forms.ModelForm):
    """Form for creating and updating devices"""
    
    class Meta:
        model = Device
        fields = [
            'name', 'device_type', 'model', 'serial_number',
            'status', 'description', 'location',
            'acquisition_date', 'warranty_expiry',
            'additional_info'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'device_type': forms.Select(attrs={'class': 'form-select'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'acquisition_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'warranty_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'additional_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }
    
    def __init__(self, *args, **kwargs):
        super(DeviceForm, self).__init__(*args, **kwargs)
        self.fields['additional_info'].help_text = "Enter additional information in JSON format, or leave blank."
        self.fields['warranty_expiry'].required = False
    
    def clean_additional_info(self):
        data = self.cleaned_data['additional_info']
        if not data:
            return {}
        
        if isinstance(data, str):
            try:
                return eval(data)  # Convert string representation to dict
            except:
                raise forms.ValidationError("Invalid JSON format")
        return data


class MaintenanceRecordForm(forms.ModelForm):
    """Form for creating and updating maintenance records"""
    
    class Meta:
        model = MaintenanceRecord
        fields = [
            'maintenance_date', 'maintenance_type', 'description',
            'performed_by', 'cost', 'next_maintenance_date'
        ]
        widgets = {
            'maintenance_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'maintenance_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'performed_by': forms.TextInput(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'next_maintenance_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
        }
    
    def __init__(self, *args, **kwargs):
        super(MaintenanceRecordForm, self).__init__(*args, **kwargs)
        self.fields['next_maintenance_date'].required = False
        self.fields['cost'].required = False
        
        # Set default maintenance date to now
        if not kwargs.get('instance'):
            self.initial['maintenance_date'] = timezone.now().strftime('%Y-%m-%dT%H:%M')


class DeviceTypeForm(forms.ModelForm):
    """Form for creating and updating device types"""
    
    class Meta:
        model = DeviceType
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }
