from django import forms
from .models import Category, Product
from accounts.models import CustomUser

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

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'userid', 'email', 'first_name', 'last_name', 'company', 'gender',
            'birth_date', 'phone_number', 'mobile_number', 'address', 'homepage',
            'recommender_id', 'additional_info'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),  # 생년월일을 date picker로 표시
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 선택적 필드 설정
        self.fields['homepage'].required = False
        self.fields['recommender_id'].required = False
        self.fields['additional_info'].required = False
        self.fields['birth_date'].required = False  # 생년월일 선택적 입력