from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from .models import Category, Product
from .forms import CategoryUploadForm, ProductForm
import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Category
from .forms import CategoryUploadForm
from .forms import ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from urllib.parse import unquote

# Create your views here.
logger = logging.getLogger(__name__)

def main_home(request):
        # 관리자 추천 상품 (최신 업데이트 순)
    admin_recommended_products = Product.objects.filter(is_admin_recommended=True).order_by('-updated_at')[:8]

    # 신규 업데이트 상품 (최신 업데이트 순)
    newly_updated_products = Product.objects.order_by('-updated_at')[:8]

    # 전체 상품 (최신 업데이트 순)
    all_products = Product.objects.order_by('-updated_at')[:8]

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
    
    return render(request, 'main_home.html', {'form': form, 'admin_recommended_products': admin_recommended_products,
        'newly_updated_products': newly_updated_products,
        'all_products': all_products})

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
                    return redirect('upload_category')
                else:
                    return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
            except Category.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '카테고리가 존재하지 않습니다.'}, status=404)

        elif action == "add":  # 등록 작업
            form = CategoryUploadForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('upload_category')
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

        return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)

    else:  # GET 요청 처리
        form = CategoryUploadForm()
        categories = Category.objects.filter(parent__isnull=True)
        return render(request, 'category_upload.html', {'form': form, 'categorys': categories})



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

def category_detail(request, category_name=None):
    # 정렬 기준 가져오기 (기본값: 날짜순)
    sort_option = request.GET.get('sort', 'updated_at')
    order_by = '-views' if sort_option == 'views' else '-updated_at'

    # Category 객체 가져오기
    if category_name:  # 특정 카테고리가 지정된 경우
        # URL 디코딩
        category_name = unquote(category_name)
        category = get_object_or_404(Category, name__iexact=category_name.strip())
        products = Product.objects.filter(category=category).order_by(order_by)

        # 제목 생성
        if category.parent:  # 하위 카테고리가 있는 경우
            title = f"{category.parent.name} > {category.name}"
        else:  # 상위 카테고리만 있는 경우
            title = category.name

        # 템플릿 선택
        template_name = "사진_게시판.html" if category.content_type == "사진" else "글_게시판.html"
    else:
        products = Product.objects.all().order_by(order_by)
        category = None
        title = "전체 상품"
        template_name = "사진_게시판.html"  # 기본 템플릿 설정

    # 템플릿에 context 전달
    context = {
        'category': category,
        'products': products,
        'title': title,
        'sort_option': sort_option,
    }

    return render(request, template_name, context)


def setting(request):
    return render(request, 'setting.html')

def product_upload(request):
    if request.method == 'POST':
        child_category_id = request.POST.get('child_category')
        parent_category_id = request.POST.get('parent_category')
        print("선택된 하위 카테고리 ID:", child_category_id)


        # 하위 카테고리 확인
        if not child_category_id:
            category = get_object_or_404(Category, id=parent_category_id)
        else:
            category = get_object_or_404(Category, id=child_category_id)

        print("카테고리", category)

        # 하위 카테고리 객체 가져오기
        #child_category = get_object_or_404(Category, id=child_category_id)

        # POST 데이터를 수정하여 category 필드를 추가
        post_data = request.POST.copy()
        post_data['category'] = category.id

        # 수정된 POST 데이터를 사용하여 폼 생성
        form = ProductForm(post_data, request.FILES)
        print("수정된 폼 데이터:", form.data)  # 수정된 데이터 확인
        print("POST 데이터:", post_data)  # 수정된 POST 데이터 출력
        if form.is_valid():
            product = form.save(commit=False)
            product.category = category  # 하위 카테고리를 직접 매핑
            product.save()
            return redirect('product_list')
        else:
            return render(request, '상품업로드.html', {'form': form, 'error': '폼 유효성 검사를 통과하지 못했습니다.'})

    return render(request, '상품업로드.html', {'form': ProductForm()})


def product_list(request):
    #검색어 가져오기
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')

    #기본 상품 쿼리셋
    products = Product.objects.all()

    #카테고리 필터링:
    if category_id:
        products = products.filter(category_id=category_id)
    
    #검색 필터링
    if search_query:
        products = products.filter(title__icontains=search_query)
    
    # 페이징 설정 (20개씩 표시)
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 모든 카테고리 가져오기
    #all_categories = Category.objects.all()
    parent_categories = Category.objects.filter(parent__isnull=True)
    return render(request, '전체상품리스트.html', {'page_obj': page_obj,
        'parent_categories': parent_categories,
        'search_query': search_query,
        'category_id': category_id,})

def get_child_categories(request, parent_id):
    if request.method == "GET":
        child_categories = Category.objects.filter(parent_id=parent_id).values('id', 'name')
        print(list(child_categories))
        return JsonResponse(list(child_categories), safe=False)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    print("product", product)

    if request.method == "POST":
        print("POST 데이터:", request.POST)
        print("FILES 데이터:", request.FILES)
        form = ProductForm(request.POST, request.FILES, instance=product)
        #print(form)
        if form.is_valid():
            form.save()
            messages.success(request, "상품이 성공적으로 수정되었습니다.")
            return redirect('product_list')
        else:
            print("폼 에러:", form.errors)  # 폼 에러 출력
    else:
        form = ProductForm(instance=product)

    parent_categories = Category.objects.filter(parent__isnull=True)
    child_categories = Category.objects.filter(parent=product.category.parent) if product.category else []
    return render(request, '상품수정.html', {'form': form, 'product': product,'parent_categories': parent_categories,
        'child_categories': child_categories,
        'selected_parent': product.category.parent.id if product.category and product.category.parent else None,
        'selected_child': product.category.id if product.category else None,})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, "상품이 성공적으로 삭제되었습니다.")
    return redirect('product_list')

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.views += 1  # 조회수 증가
    product.save()
    return render(request, '상세_페이지.html', {'product': product})

def company_introduce(request):
    return render(request, '회사소개.html')

def my_page(request):
    User = get_user_model()
    user = User.objects.get(pk=request.user.pk)  # 새로 쿼리
    print(f"birth_date from DB: {user.birth_date}")  # 확인
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('my_page')
    else:
        form = ProfileUpdateForm(instance=user)
    return render(request, 'my_page.html', {'form': form})