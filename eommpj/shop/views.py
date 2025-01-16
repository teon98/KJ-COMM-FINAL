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
from django.db.models import Q  # Q 객체 사용
from .models import Product, Cart, Order
from uuid import uuid4
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import AnonymousUser

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

    # 쿠키 설정
    recently_viewed = request.COOKIES.get('recently_viewed', '')  # 쿠키 읽기
    viewed_list = recently_viewed.split(',') if recently_viewed else []

    if str(pk) in viewed_list:
        viewed_list.remove(str(pk))  # 중복 제거
    viewed_list.insert(0, str(pk))  # 맨 앞에 추가

    if len(viewed_list) > 3:
        viewed_list = viewed_list[:3]

    # 템플릿 렌더링
    response = render(request, '상세_페이지.html', {'product': product})
    response.set_cookie('recently_viewed', ','.join(viewed_list), max_age=7*24*60*60)  # 쿠키 유지 기간: 7일
    product.save()
    return response

def company_introduce(request):
    return render(request, '회사소개.html')

def use_info(request):
    return render(request, '이용안내.html')

def usage_policy(request):
    return render(request, '이용약관.html')

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

def product_search(request):
    query = request.GET.get('q', '').strip()  # 검색어 가져오기 및 공백 제거
    print(f"검색어: {query}")  # 디버깅 출력
    
    products = Product.objects.filter(title__icontains=query) if query else Product.objects.none()
    print(f"검색 결과: {products}")  # 디버깅 출력
    
    return render(request, 'product_search.html', {
        'products': products,
        'query': query,
    })

def payment_option(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    print(f"Request Method: {request.method}")  # 요청 메서드 확인
    print(f"POST Data: {request.POST}")  # POST 데이터 확인

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        if payment_method not in ['bank_transfer', 'credit_card']:
            messages.error(request, "유효하지 않은 결제 방식입니다.")
            return redirect('payment_option', product_id=product_id)

        # 주문 생성
        cart_group_id = str(uuid4())
        quantity = 1

        Order.objects.create(
            user=request.user,
            cart_group_id=cart_group_id,
            product=product,
            quantity=quantity,
            total_price=product.price,
            payment_method=payment_method,
            payment_status='pending' if payment_method == 'bank_transfer' else 'completed',
        )

        # 장바구니 추가
        request.POST = request.POST.copy()
        request.POST['quantity'] = str(quantity)
        add_to_cart(request, product_id)

        messages.success(request, "결제가 완료되었습니다.")
        return redirect('cart_view')

    return render(request, '결제방식_선택.html', {'product': product, 'product_id': product_id})

#장바구니 추가
def add_to_cart(request, product_id):
    print(f"add_to_cart called with Product ID: {product_id}")
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    # 기존 장바구니 항목이 있는지 확인
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += quantity  # 기존 항목에 수량 추가
    else:
        cart_item.quantity = quantity
    cart_item.save()

    print(f"Added to cart: {cart_item}")
    print(f"추가 할때는 안뜨나? {request.user.username}: {Cart.objects.filter(user=request.user)}")

    return redirect('cart_view')  # 장바구니 페이지로 리다이렉트

#장바구니 보기
@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    for item in cart_items:
        print(f"카트 아이템: {item.id}, 상품: {item.product.title}, 수량: {item.quantity}")
    return render(request, 'cart.html', {'cart_items': cart_items})

#장바구니 수정
def update_cart(request, cart_item_id):
    print(f"Updating Cart Item ID: {cart_item_id}")
    print(f"POST Data: {request.POST}")

    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    new_quantity = int(request.POST.get('quantity', 1))
    if new_quantity > 0:
        cart_item.quantity = new_quantity
        cart_item.save()
        print(f"Cart Item Updated: {cart_item.id}, New Quantity: {cart_item.quantity}")
    else:
        cart_item.delete()
        print(f"Cart Item Deleted: {cart_item.id}")
    return redirect('cart_view')


@login_required
def cart_remove(request, cart_item_id):
    """
    장바구니에서 특정 상품 삭제
    """
    try:
        # 현재 사용자의 장바구니에서 해당 상품 삭제
        cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
        cart_item.delete()
        messages.success(request, "장바구니에서 상품이 삭제되었습니다.")
    except Cart.DoesNotExist:
        messages.error(request, "해당 상품이 장바구니에 없습니다.")
    
    return redirect('cart_view')  # 장바구니 페이지로 리디렉트


#바로 구매(장바구니에 추가 후 장바구니로 이동)
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    # 장바구니에 추가
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()

    return redirect('checkout')  # 결제 페이지로 이동

def checkout(request):
    payment_method = request.POST.get('payment_method')

    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Ajax 요청에 대해 JSON 응답 반환
            return JsonResponse({'error': '로그인이 필요합니다.'}, status=401)
        else:
            # 일반 요청에 대해 로그인 페이지로 리디렉션
            messages.error(request, "로그인이 필요합니다.")
            return redirect('/')
        
    cart_items = Cart.objects.filter(user=request.user)

    # 장바구니 그룹 ID 생성
    cart_group_id = str(uuid4())

    total_price = 0
    for item in cart_items:
        total_price += item.total_price()

        # 주문 생성
        Order.objects.create(
            user=request.user,
            cart_group_id=cart_group_id,
            product=item.product,
            quantity=item.quantity,
            total_price=item.total_price(),
            payment_method='bank_transfer',  # 기본값: 무통장 입금
        )

    # 장바구니 비우기
    cart_items.delete()
    
    # 무통장 결제 처리
    if payment_method == 'bank_transfer':
        messages.success(request, "무통장 결제가 선택되었습니다. 장바구니로 이동합니다.")
        return redirect('cart_view')  # 장바구니 페이지로 리디렉션

    
    return render(request, 'checkout.html', {
        'cart_group_id': cart_group_id,
        'total_price': total_price,
    })

#주문정보 관리자 페이지 뷰
@staff_member_required
def admin_order_list(request):
    orders = Order.objects.all()

    # 필터링 (날짜별, 그룹 ID별, 사용자 이름별)
    user_query = request.GET.get('user', '')
    group_query = request.GET.get('cart_group_id', '')
    date_query = request.GET.get('date', '')

    if user_query:
        orders = orders.filter(user__username__icontains=user_query)
    if group_query:
        orders = orders.filter(cart_group_id=group_query)
    if date_query:
        orders = orders.filter(order_date__date=date_query)

    return render(request, 'admin_order_list.html', {'orders': orders})

#주문 상태 업데이트
@staff_member_required
def update_payment_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('payment_status')
    if new_status in dict(Order.PAYMENT_STATUS_CHOICES).keys():
        order.payment_status = new_status
        order.save()
    return redirect('admin_order_list')

#장바구니 한번에 초기화
def clear_cart(request):
    Cart.objects.filter(user=request.user).delete()
    return redirect('cart_view')

#결제 완료 화면
def checkout_complete(request, cart_group_id):
    orders = Order.objects.filter(cart_group_id=cart_group_id, user=request.user)
    return render(request, 'checkout_complete.html', {'orders': orders})

#사용자 자기 주문 내역
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'my_orders.html', {'orders': orders})
