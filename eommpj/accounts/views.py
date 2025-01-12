from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from accounts.form import LoginForm
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from .models import CustomUser
from django.contrib.auth import get_user_model
from .form import RegisterForm

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username') 
        password = request.POST.get('password')
        print(f"입력된 사용자명: {username}, 비밀번호: {password}")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            print(f"User {user.username} logged in successfully.")  # 성공 로그
            return redirect('/')
        else:
            print("로그인 실패: 사용자 이름 또는 비밀번호가 잘못되었습니다.")  # 실패 로그
            return render(request, 'base.html', {'error': 'Invalid username or password'})
    return render(request, 'base.html')


def user_logout(request):
    logout(request) #세션을 종료하고 로그아웃
    return redirect('/')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        print("폼 데이터:", request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.save()
                print(f"저장된 사용자 birth_date: {user.birth_date}")  # 확인
                login(request, user)  # 회원가입 후 자동 로그인
                return redirect('my_page')  # 마이페이지로 리디렉션
            except Exception as e:
                print(f"사용자 저장 중 오류: {e}")  # 디버그용 로그
                form.add_error(None, '사용자 저장 중 오류가 발생했습니다.')
        else:
            print(f"폼 유효성 검사 실패: {form.errors}")  # 디버그용 로그
    else:
        form = RegisterForm(initial={
            'email': '',
            'first_name': '',
            'last_name': ''
        })

    return render(request, 'accounts/register.html', {'form': form})


def register_form(request):
    register_username = request.GET.get('register_username', 'Anonymous')

    return render(request, 'accounts/register2.html', {'register_username': register_username})

User = get_user_model()


def check_userid(request):
    userid = request.GET.get('userid', None)
    if not userid:
        return JsonResponse({'error': '아이디를 입력해주세요.'}, status=400)

    exists = User.objects.filter(userid=userid).exists()
    return JsonResponse({'exists': exists})