from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from accounts.form import LoginForm
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from .models import CustomUser
from .form import RegisterForm
from django.contrib import messages
from django.db.models import Count
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.core.mail import send_mail
from urllib.parse import quote
from django.contrib.auth.views import LoginView


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
            return render(request, 'accounts/login.html', {'error': 'Invalid username or password'})
    return render(request, 'accounts/login.html')


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

def manage_users(request):
    # 필터링
    user_type_filter = request.GET.get('user_type')
    if user_type_filter in ['admin', 'user']:
        users = User.objects.filter(user_type=user_type_filter)
    else:
        users = User.objects.all()

    # 통계
    today = datetime.today()
    start_of_this_month = today.replace(day=1)
    start_of_last_month = (start_of_this_month - timedelta(days=1)).replace(day=1)

    this_month_users = users.filter(date_joined__gte=start_of_this_month).count()
    last_month_users = users.filter(date_joined__gte=start_of_last_month, date_joined__lt=start_of_this_month).count()

    # 페이지네이션
    paginator = Paginator(users, 20)  # 페이지당 20명
    page = request.GET.get('page')

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    context = {
        'users': users,
        'this_month_users': this_month_users,
        'last_month_users': last_month_users,
        'user_type_filter': user_type_filter,
    }
    return render(request, 'accounts/manage_users.html', context)

def update_user_role(request, user_id):  # user_id로 변경
    print("메타몽", request, user_id)
    if request.method == 'POST':
        try:
            new_role = request.POST.get('user_type')
            user = User.objects.get(pk=user_id)  # user_id 사용
            user.user_type = new_role
            user.save()
            return JsonResponse({'message': '사용자 권한이 변경 완료 되었습니다.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def delete_user(request, user_id):
    if request.method == 'POST':
        try:
            user = User.objects.get(pk=user_id)  # id를 기준으로 사용자 조회
            user.delete()
            return JsonResponse({'message': '사용자 삭제가 완료 되었습니다.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

# 비밀번호 찾기 폼을 보여주는 뷰
def password_find_form(request):
    if request.method == "POST":
        email = request.POST.get('email')  # 사용자가 입력한 이메일
        if email:
            return redirect('password_find_with_email', email=email)
        else:
            return HttpResponse("이메일을 입력해 주세요.", status=400)
    return render(request, 'registration/password_find.html')

# 이메일을 통해 비밀번호 재설정하는 뷰
def password_find_process(request, email):
    if request.method == "GET":
        users = User.objects.filter(email=email)
        if users.exists():
            for user in users:
                new_password = User.objects.make_random_password()
                user.set_password(new_password)
                user.save()

                send_mail(
                    '비밀번호 찾기 요청',
                    f'귀하의 새 비밀번호는: {new_password}',
                    'your-email@example.com',
                    [email],
                    fail_silently=False,
                )
            return HttpResponse("비밀번호가 이메일로 전송되었습니다.")
        else:
            return HttpResponse("해당 이메일을 찾을 수 없습니다.", status=404)
    else:
        return HttpResponse("잘못된 요청입니다.", status=400)
    
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'  # 사용할 템플릿 경로