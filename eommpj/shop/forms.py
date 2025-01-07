from django import forms
from .models import Category, Product

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

class ProductForm(forms.ModelForm):
    parent_category = forms.ModelChoiceField(
        queryset=Category.objects.filter(parent__isnull=True),  # 상위 카테고리만
        label="상위 카테고리",
        required=False,
        widget=forms.Select(attrs={'id': 'parent-category'})  # JavaScript에서 활용할 ID
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="카테고리",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Product
        fields = [
            'category', 'header_image', 'detail_image', 'title', 'price',
            'price_detail', 'origin', 'brand', 'manufacturer', 
            'is_free_shipping', 'is_admin_recommended',
        ]
        widgets = {
            'price_detail': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={
                'step': 1000,  # 1,000 단위로 증가
                'min': 0,      # 최소값 설정
            }),
        }