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

    class Meta:
        db_table = 'category' 

    def __str__(self):
        return self.name