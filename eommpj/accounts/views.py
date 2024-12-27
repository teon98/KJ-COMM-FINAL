from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from accounts.form import LoginForm
from django.contrib.auth import authenticate, login

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # 회원가입 후 로그인 페이지로 이동
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.methd == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                if user.user_type == "admin":
                    return redirect("admin_dashboard") #관리자 페이지
                else:
                    return redirect("user_dashboard") #일반 사용자 페이지
    else:
        form=LoginForm()
    return render(request, "login.html", {"form", form})