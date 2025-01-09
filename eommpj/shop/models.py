from django.db import models
from django.utils.text import slugify
import os
from django.utils.timezone import now

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