from django.db import models
from django.utils.text import slugify
import os

def category_image_upload_path(instance, filename):
    # 파일 확장자 추출
    ext = filename.split('.')[-1]
    # 안전한 파일 이름 생성 (slugify로 한글 제거)
    safe_filename = slugify(os.path.splitext(filename)[0])
    return f"categories/{safe_filename}.{ext}"

class Category(models.Model):
    name = models.CharField(max_length=255) #카테고리 이름
    image = models.ImageField(upload_to=category_image_upload_path, blank=True, null=True)  # 이미지 업로드
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subcategories')
    content_type = models.CharField(max_length=255, default='글') #글 타입('글','이미지')

    class Meta:
        db_table = 'category' 

    def __str__(self):
        # 상위 카테고리 > 하위 카테고리 형식으로 표시
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    header_image = models.ImageField(upload_to='products/headers/')
    detail_image = models.ImageField(upload_to='products/details/')
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    price_detail = models.TextField()
    origin = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    is_free_shipping = models.BooleanField(default=False)
    is_admin_recommended = models.BooleanField(default=False)

    def __str__(self):
        return self.title