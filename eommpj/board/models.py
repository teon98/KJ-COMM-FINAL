from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class BoardCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)  # 카테고리 이름
    description = models.TextField(blank=True, null=True)  # 카테고리 설명

    class Meta:
        db_table = 'board_category'
        ordering = ['name']  # 이름 순으로 정렬

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_CHOICES = [
        ('대기', '대기'),
        ('처리 중', '처리 중'),
        ('처리 완료', '처리 완료'),
    ]

    category = models.ForeignKey(BoardCategory, on_delete=models.CASCADE, related_name="posts")  # 카테고리
    title = models.CharField(max_length=200)  # 제목
    content = models.TextField()  # 내용
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  # 작성일
    updated_at = models.DateTimeField(auto_now=True)  # 수정일
    views = models.PositiveIntegerField(default=0)  # 조회수
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='대기')  # 진행사항

    def __str__(self):
        return self.title