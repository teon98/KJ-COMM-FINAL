from .models import Product
import requests
from django.conf import settings
from uuid import uuid4

def recently_viewed_products(request):
    """
    Retrieve recently viewed products from cookies.
    """
    recently_viewed = request.COOKIES.get('recently_viewed', '')
    if recently_viewed:
        product_ids = recently_viewed.split(',')
        products = Product.objects.filter(id__in=product_ids)
        return sorted(products, key=lambda p: product_ids.index(str(p.id)))
    return []

import requests
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from uuid import uuid4

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
    if result["code"] == 0:
        return result["response"]["access_token"]
    else:
        raise ValueError("아임포트 액세스 토큰 발급 실패")

# 2. 나이스페이 비인증 결제 요청 함수
def process_payment(request, cart_group_id):
    if request.method == 'POST':
        card_number = (
            request.POST.get('card_number1') +
            request.POST.get('card_number2') +
            request.POST.get('card_number3') +
            request.POST.get('card_number4')
        )
        expiry = request.POST.get('expiry')  # YYMM 형식
        birth = request.POST.get('birth')  # YYMMDD 형식
        pwd_2digit = request.POST.get('pwd_2digit')
        total_price = request.session.get('total_price', 100)

        access_token = get_access_token()

        payment_data = {
            "merchant_uid": f"order_{uuid4()}",
            "amount": total_price,
            "card_number": card_number,
            "expiry": expiry,  # YYMM 형식
            "birth": birth,  # YYMMDD 형식
            "pwd_2digit": pwd_2digit,
            "pg": "nicepay",
            "buyer_name": request.user.get_full_name(),
            "buyer_email": request.user.email,
            "buyer_tel": "01012345678",
            "name": "테스트 결제",
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            f"{IAMPORT_API_URL}/subscribe/payments/onetime",
            headers=headers,
            data=json.dumps(payment_data)
        )

        result = response.json()

        if result["code"] == 0:
            messages.success(request, "결제가 성공적으로 완료되었습니다.")
            return redirect('checkout_complete', cart_group_id=cart_group_id)
        else:
            messages.error(request, f"결제 실패: {result.get('message', '알 수 없는 오류')}")
    
    return render(request, 'payment.html', {'cart_group_id': cart_group_id})
