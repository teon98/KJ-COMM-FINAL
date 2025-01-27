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
from django.db import transaction
from django.conf import settings
from django.db import transaction
from uuid import uuid4
from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Cart, Order
from .forms import PaymentForm
import requests
import json
from iamport.client import Iamport
imp_client = Iamport(imp_key=settings.IAMPORT_API_KEY, imp_secret=settings.IAMPORT_API_SECRET)

# Create your views here.
logger = logging.getLogger(__name__)
global_quantity = 1
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

    # 기본 quantity 값 설정
    quantity = global_quantity

    if request.method == 'POST':

        quantity = int(request.POST.get('quantity'))

        print(f"결제방식 선택에서 받은 수량: {quantity}")

        payment_method = request.POST.get('payment_method')

        if payment_method not in ['bank_transfer', 'credit_card']:
            messages.error(request, "유효하지 않은 결제 방식입니다.")
            return redirect('payment_option', product_id=product_id)

        # 세션에 결제 방식 저장
        request.session['payment_method'] = payment_method

        # 장바구니에 상품 추가
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        messages.success(request, "결제 방식이 선택되었습니다. 장바구니로 이동합니다.")
        return redirect('cart_view')

    # GET 요청 처리: 기본값 유지
    print(f"GET 요청에서 기본 quantity: {quantity}")
    return render(request, '결제방식_선택.html', {'product': product, 'product_id': product_id, 'quantity': quantity})

#장바구니 추가
@login_required
def add_to_cart(request, product_id):
    print(f"add_to_cart called with Product ID: {product_id}")
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity'))
    global_quantity = quantity
    print("장바구니 수량", quantity)

    # 기존 장바구니 항목이 있는지 확인
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += quantity  # 기존 항목에 수량 추가
    else:
        cart_item.quantity = quantity
 
    cart_item.save()  # 변경사항 저장
    return redirect('cart_view')  # 장바구니 페이지로 리다이렉트

#장바구니 보기
@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)

    # 사용자 정보 가져오기
    user_profile = request.user 

    for item in cart_items:
        print(f"카트 아이템: {item.id}, 상품: {item.product.title}, 수량: {item.quantity}")
    return render(request, 'cart.html', {'cart_items': cart_items, 'user_profile': user_profile,})

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
        print(request, "해당 상품이 장바구니에 없습니다.")
    
    return redirect('cart_view')  # 장바구니 페이지로 리디렉트


#바로 구매(장바구니에 추가 후 장바구니로 이동)
@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1  # 기본 수량 설정

    print(f"바로 구매 - 받은 수량: {quantity}")

    # 장바구니에 상품 추가
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )
    if not created:
        cart_item.quantity += quantity  # 기존 항목에 수량 추가
    else:
        cart_item.quantity = quantity  # 새로 추가된 경우

    cart_item.save()

    # 장바구니 페이지로 리디렉션
    return redirect('cart_view')

@login_required
def checkout(request):
    if not request.user.is_authenticated:
        messages.error(request, "로그인이 필요합니다.")
        return redirect('/')

    # 세션에서 cart_group_id 가져오기 (중복 방지 로직 포함)
    if 'cart_group_id' not in request.session or Order.objects.filter(cart_group_id=request.session.get('cart_group_id')).exists():
        print("중복 cart_group_id 발견 또는 세션 없음, 새 ID 생성")
        while True:
            new_cart_group_id = str(uuid4())
            if not Order.objects.filter(cart_group_id=new_cart_group_id).exists():
                request.session['cart_group_id'] = new_cart_group_id
                break
    else:
        request.session['cart_group_id'] = str(uuid4())

    cart_group_id = request.session.get('cart_group_id', None)
    print("카트 그룹 아이디", cart_group_id)
    # 결제 방식 가져오기
    payment_method = request.POST.get('payment_method')
    if not payment_method:
        messages.error(request, "결제 방식을 선택해주세요.")
        return redirect('cart_view')
    print("결제방식", payment_method)

    # 사용자 장바구니 가져오기
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.error(request, "장바구니가 비어 있습니다.")
        return redirect('cart_view')
    print("장바구니",cart_items)
    total_price = sum(item.quantity * item.product.price for item in cart_items)
    total_quantity = sum(item.quantity for item in cart_items)
    print("총액", "총수량", total_price,total_quantity)

    # 트랜잭션 시작
    try:
        with transaction.atomic():
            order_list = []
            update_list = []

            for item in cart_items:
                order = Order.objects.filter(
                    user=request.user,
                    cart_group_id=cart_group_id,
                    product=item.product
                ).first()

                if order:
                    # 기존 주문이 있으면 업데이트
                    print("기존 주문 발견:", order)
                    order.quantity += item.quantity
                    order.total_price += item.quantity * item.product.price
                    update_list.append(order)
                else:
                    # 새 주문 생성
                    new_order = Order(
                        user=request.user,
                        cart_group_id=cart_group_id,
                        product=item.product,
                        quantity=item.quantity,
                        total_price=item.quantity * item.product.price,
                        payment_method=payment_method,
                        payment_status='pending' if payment_method == 'bank_transfer' else 'completed',
                    )
                    order_list.append(new_order)

            # 새 주문 항목을 먼저 데이터베이스에 저장
            if order_list:
                Order.objects.bulk_create(order_list)
                print(f"{len(order_list)}개의 주문이 새로 추가되었습니다.")

            # 기존 주문 항목 업데이트
            if update_list:
                Order.objects.bulk_update(update_list, ['quantity', 'total_price'])
                print(f"{len(update_list)}개의 주문이 업데이트되었습니다.")

            # 장바구니 비우기
            cart_items.delete()
            print("장바구니 비움 완료")

            # 세션에서 cart_group_id 제거
            if 'cart_group_id' in request.session:
                del request.session['cart_group_id']
                print("세션 cart_group_id 제거 완료")

    except Exception as e:
        print(f"결제 실패: {e}")
        messages.error(request, f"결제 중 오류가 발생했습니다: {e}")
        return redirect('cart_view')

    # 결제 방식에 따른 리디렉션 처리
    if payment_method == 'bank_transfer':
        messages.success(request, "무통장 결제가 선택되었습니다. 안내 페이지로 이동합니다.")
        return redirect('bank_transfer_guide', cart_group_id=cart_group_id)

    messages.success(request, "신용카드 결제가 선택되었습니다.")
    request.session['total_price'] = float(total_price)
    return redirect('payment_view', cart_group_id=cart_group_id)

def bank_transfer_guide(request, cart_group_id):
    return render(request, 'bank_transfer_guide.html', {'cart_group_id': cart_group_id})

#주문정보 관리자 페이지 뷰
#@staff_member_required
def admin_order_list(request):
    orders = Order.objects.all()

    # 필터링 (날짜별, 장바구니 그룹 ID(cart_group_id)별, 사용자 ID별)
    user_query = request.GET.get('user', '').strip()
    group_query = request.GET.get('cart_group_id', '').strip()
    date_query = request.GET.get('date', '').strip()

    if user_query:
        orders = orders.filter(user__userid__icontains=user_query)  # CustomUser의 userid 필드 기준으로 검색
    if group_query:
        orders = orders.filter(cart_group_id__icontains=group_query)  # 포함 검색
    if date_query:
        orders = orders.filter(order_date__date=date_query)  # 날짜 형식 필터링

    if not orders.exists():
        no_results = True  # 검색 결과 없을 때 표시용 변수
    else:
        no_results = False

    return render(request, 'admin_order_list.html', {
        'orders': orders,
        'no_results': no_results,
        'user_query': user_query,
        'group_query': group_query,
        'date_query': date_query
    })


def admin_order_detail(request, cart_group_id):
    orders = Order.objects.filter(cart_group_id=cart_group_id)
    return render(request, 'admin_order_detail.html', {'orders': orders})

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
#def checkout_complete(request, cart_group_id):
#    orders = Order.objects.filter(cart_group_id=cart_group_id, user=request.user)
#    return render(request, 'payment.html', {'orders': orders})

#사용자 자기 주문 내역
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'my_orders.html', {'orders': orders})


IAMPORT_API_URL = "https://api.iamport.kr"


# 1. 아임포트 액세스 토큰 발급 함수
def get_access_token():
    response = requests.post(
        f"{IAMPORT_API_URL}/users/getToken",
        json={
            "imp_key": settings.IAMPORT_API_KEY,
            "imp_secret": settings.IAMPORT_API_SECRET,
        }
    )
    result = response.json()
    if result.get("code") == 0:
        return result["response"]["access_token"]
    else:
        raise print("아임포트 액세스 토큰 발급 실패: " + result.get("message", "알 수 없는 오류"))


# 2. 결제 요청 로직
def payment_view(request, cart_group_id):
    total_price = request.session.get('total_price', 0)

    if request.method == 'POST':
        # 카드 번호를 4개의 입력 필드에서 받아 조합
        card_number = (
            request.POST.get('card_number1', '') +
            request.POST.get('card_number2', '') +
            request.POST.get('card_number3', '') +
            request.POST.get('card_number4', '')
        )
        expiry = request.POST.get('expiry')  # YYMM 형식 (예: 2401)
        birth = request.POST.get('birth')  # YYMMDD 형식
        pwd_2digit = request.POST.get('pwd_2digit')

        # 필수 입력 확인
        if not (card_number and expiry and birth and pwd_2digit):
            print(request, "모든 필수 입력 항목을 작성해주세요.")
            return render(request, 'payment.html', {'total_price': total_price, 'cart_group_id': cart_group_id})

        try:
            # 아임포트 토큰 발급
            access_token = get_access_token()

            payment_data = {
                "merchant_uid": f"order_{uuid4()}",
                "amount": total_price,
                "card_number": card_number,
                "expiry": expiry,
                "birth": birth,
                "pwd_2digit": pwd_2digit,
                "pg": "nice",
                "buyer_name": request.user.get_full_name(),
                "buyer_email": request.user.email,
                "buyer_tel": "01012345678",
                "name": "상품 결제",
            }

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            # 결제 요청 보내기
            response = requests.post(
                f"{IAMPORT_API_URL}/subscribe/payments/onetime",
                headers=headers,
                data=json.dumps(payment_data)
            )

            result = response.json()
            print("결제 응답:", result)  # 디버깅 용도

            if result.get("code") == 0 and result["response"]["status"] == "paid":
                print(request, "결제가 성공적으로 완료되었습니다.")
                return redirect('checkout_complete', cart_group_id=cart_group_id)
            else:
                print(request, f"결제 실패: {result.get('message', '알 수 없는 오류')}")

        except Exception as e:
            print(request, f"결제 중 오류 발생: {str(e)}")

    return render(request, 'payment.html', {'total_price': total_price, 'cart_group_id': cart_group_id})


# 3. 결제 완료 페이지
def checkout_complete(request, cart_group_id):
    orders = Order.objects.filter(cart_group_id=cart_group_id, user=request.user)

    # 세션 정보 삭제
    if 'total_price' in request.session:
        del request.session['total_price']
    if 'payment_method' in request.session:
        del request.session['payment_method']

    return render(request, 'checkout_complete.html', {'orders': orders})

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    
    # 주문 상태 필터링
    bank_transfer_orders = orders.filter(payment_method='bank_transfer')
    credit_card_orders = orders.filter(payment_method='credit_card')

    context = {
        'bank_transfer_orders': bank_transfer_orders,
        'credit_card_orders': credit_card_orders,
    }

    return render(request, 'my_orders.html', context)
