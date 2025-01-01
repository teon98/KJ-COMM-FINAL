from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required

# Create your views here.

def main_home(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('/')  # 로그인 후 홈 화면으로 리디렉션

            #사용자 타입에 따라 리다이렉션 또는 정보 전달
            if user.user_type == "admin":
                role = "관리자"
            else:
                role = "사용자"

            #로그인 후 메인 화면에 사용자 타입 표시
            return render(request, 'main_home.html', {'form': form, 'role': role})
    
    else:
        form = AuthenticationForm()
    return render(request, 'main_home.html', {'form': form})

@login_required
def accounts_info(request):
    if request.user.user_tyoe == 'admin':
        role="관리자"
    else:
        role="사용자"

    return render(request, 'base.html', {'role': role})