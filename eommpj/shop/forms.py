from django import forms
from .models import Category

class CategoryUploadForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'image', 'parent', 'content_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = Category.objects.filter(parent__isnull = True)

    CONTENT_TYPE_CHOICES = [
        ('글', '글'), 
        ('사진', '사진'),
    ]
    content_type = forms.ChoiceField(choices=CONTENT_TYPE_CHOICES)
