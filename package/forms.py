from django.forms import ModelForm
from .models import *

class PackageForm(ModelForm):
    class Meta:
        model=Package
        fields='__all__'
        