from django.forms import ModelForm

from .models import *

class ProjectFrom(ModelForm):
    class Meta:
        model = Project
        fields = ['group', 'name']