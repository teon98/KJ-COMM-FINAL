from django import forms
from django.contrib.auth import authenticate
from .models import CustomUser

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
    
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="비밀번호")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="비밀번호 확인")

    class Meta:
        model = CustomUser
        fields = [
            'userid', 'email', 'password', 'password_confirm', 'first_name', 'last_name',
            'company', 'gender', 'birth_date', 'phone_number', 'mobile_number',
            'address', 'homepage', 'recommender_id', 'additional_info',
        ]

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        print(f"폼에서 처리된 birth_date: {birth_date}")  # 확인
        return birth_date
    
    def clean_userid(self):
        userid = self.cleaned_data.get('userid')
        if CustomUser.objects.filter(userid=userid).exists():
            raise forms.ValidationError('이미 사용 중인 아이디입니다.')
        return userid

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')

        # 비밀번호 확인
        if password != password_confirm:
            self.add_error('password_confirm', '비밀번호가 일치하지 않습니다.')

        # 이름 확인
        if not first_name or not last_name:
            raise forms.ValidationError('이름과 성을 모두 입력해야 합니다.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = f"{self.cleaned_data['first_name']}.{self.cleaned_data['last_name']}".lower()
        user.set_password(self.cleaned_data['password'])  # 비밀번호 암호화 저장
        if commit:
            user.save()
        return user
