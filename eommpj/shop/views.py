from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from .models import Category
from .forms import CategoryUploadForm
import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
# Create your views here.
logger = logging.getLogger(__name__)

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

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})

def category_upload(request):
    if request.method == "POST":
        action = request.POST.get('action')  # 어떤 버튼이 눌렸는지 확인
        category_id = request.POST.get('id')  # 수정 시 전달되는 ID

        if action == "edit" and category_id:  # 수정 작업
            try:
                category = Category.objects.get(id=category_id)
                form = CategoryUploadForm(request.POST, request.FILES, instance=category)
                if form.is_valid():
                    form.save()
                    return JsonResponse({'status': 'success', 'message': '카테고리가 수정되었습니다.'}, status=200)
                else:
                    return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
            except Category.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '카테고리가 존재하지 않습니다.'}, status=404)

        elif action == "add":  # 등록 작업
            form = CategoryUploadForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success', 'message': '카테고리가 등록되었습니다.'}, status=200)
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

        return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)

    else:  # GET 요청 처리
        form = CategoryUploadForm()
        categories = Category.objects.filter(parent__isnull=True)
        return render(request, 'category_upload.html', {'form': form, 'categorys': categories})

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Category
from .forms import CategoryUploadForm

# 카테고리 수정 뷰
def category_edit(request, id):
    if request.method == "POST":
        category = get_object_or_404(Category, id=id)
        form = CategoryUploadForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': '카테고리가 수정되었습니다.'}, status=200)
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': '잘못된 요청입니다.'}, status=400)

@csrf_exempt
def delete_category(request, category_id):
    if request.method == 'POST':
        try:
            category = Category.objects.get(id=category_id)
            category.delete()
            return JsonResponse({'status': 'success'}, status=200)
        except Category.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Category not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)