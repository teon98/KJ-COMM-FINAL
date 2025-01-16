from django.db import models
from django.utils.text import slugify
import os
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser
from django.conf import settings

def category_image_upload_path(instance, filename):
    # 파일 확장자 추출
    ext = filename.split('.')[-1]
    # 안전한 파일 이름 생성 (slugify로 한글 제거)
    safe_filename = slugify(os.path.splitext(filename)[0])
    return f"categories/{safe_filename}.{ext}"

def safe_file_upload_path_headers(instance, filename):
    name, ext = os.path.splitext(filename)
    safe_name = slugify(name)  # 파일 이름을 안전한 ASCII 문자열로 변환
    return f"products/headers/{safe_name}{ext}"

def safe_file_upload_path_details(instance, filename):
    name, ext = os.path.splitext(filename)
    safe_name = slugify(name)  # 파일 이름을 안전한 ASCII 문자열로 변환
    return f"products/details/{safe_name}{ext}"

class Category(models.Model):
    name = models.CharField(max_length=255) #카테고리 이름
    image = models.ImageField(upload_to=category_image_upload_path, blank=True, null=True)  # 이미지 업로드
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subcategories')
    content_type = models.CharField(max_length=255, default='글') #글 타입('글','이미지')

    class Meta:
        db_table = 'category' 
        ordering = ['id']

    def __str__(self):
        # 상위 카테고리 > 하위 카테고리 형식으로 표시
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

class Product(models.Model):
    class Meta:
        ordering = ['-updated_at']
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products',null=True, blank=True)
    header_image = models.ImageField(upload_to=safe_file_upload_path_headers)
    detail_image = models.ImageField(upload_to=safe_file_upload_path_details)
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    price_detail = models.TextField(blank=True, null=True)
    origin = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    is_free_shipping = models.BooleanField(default=False)
    is_admin_recommended = models.BooleanField(default=False)
    updated_at = models.DateTimeField(default=now, blank=True, null=True)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

#주문정보
class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('bank_transfer', '무통장 입금'),
        ('credit_card', '카드 결제'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', '입금 전'),
        ('completed', '입금 완료'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shop_orders')
    cart_group_id = models.CharField(max_length=100, unique=True)  # 장바구니 그룹 ID
    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    order_date = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.cart_group_id} - {self.user.username} - {self.payment_status}"

#장바구니
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.user.username} - {self.product.title} x {self.quantity}"

    def total_price(self):
        return self.quantity * self.product.price