from django import forms
from .models import Category

class CategoryUploadForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'image', 'parent']

        
