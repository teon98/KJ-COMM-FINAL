from django import forms
from .models import Post, BoardCategory
from django_summernote.fields import SummernoteTextField


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['category', 'title', 'content']
        
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': '제목을 입력하세요'}),
            'category': forms.Select(),  # 카테고리 선택
        }

class BoardCategoryForm(forms.ModelForm):
    class Meta:
        model = BoardCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': '카테고리 이름을 입력하세요'}),
            'description': forms.Textarea(attrs={'placeholder': '카테고리 설명을 입력하세요'}),
        }