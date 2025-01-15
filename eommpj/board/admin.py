from django.contrib import admin
from .models import BoardCategory, Post

@admin.register(BoardCategory)
class BoardCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)  # 카테고리 목록에 표시할 필드

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'created_at', 'views')
