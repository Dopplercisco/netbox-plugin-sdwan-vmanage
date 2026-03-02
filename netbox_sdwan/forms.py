from django import forms

from .models import SDWANMapping


class SDWANMappingForm(forms.ModelForm):
    """Form for creating or editing an SDWANMapping."""

    class Meta:
        model = SDWANMapping
        fields = ['config_group_name', 'rp_serial']
        widgets = {
            'config_group_name': forms.TextInput(attrs={'class': 'form-control'}),
            'rp_serial': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'config_group_name': 'Config Group Name',
            'rp_serial': 'RP Serial',
        }
