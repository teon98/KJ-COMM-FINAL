from django import forms
from django.contrib.auth import authenticate

class LoginForm(forms.Form):
    username = forms.CharField(max_length = 255, label="아이디")
    password = forms.CharField(widget=forms.PasswordInput, label = "비밀번호")

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        user = authenticate(username = username, password=password)
        if not user:
            raise forms.ValidationError("아이디 또는 비밀번호가 틀렸습니다.")
        return cleaned_data