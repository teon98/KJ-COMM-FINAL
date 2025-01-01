from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from accounts.form import LoginForm
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        print(username, password)
        print(user)
        if user is not None:
            login(request, user)
            print(f"User {user.username} logged in successfully.")  # 확인용 출력
            return redirect('/')
        else:
            return render(request, 'base.html', {'error': 'Invalid username or password'})
    return render(request, 'base.html')

def user_logout(request):
    logout(request) #세션을 종료하고 로그아웃
    return redirect('/')

def register(request):
    return render(request, 'accounts/register.html' )