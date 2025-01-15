from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),  # 게시글 목록
    path('<int:pk>/', views.post_detail, name='post_detail'),  # 게시글 상세
    path('new/', views.post_create, name='post_create'),  # 게시글 작성
    path('<int:pk>/update/', views.post_update, name='post_update'),  # 게시글 수정
    path('<int:pk>/delete/', views.post_delete, name='post_delete'),
    path('category/<int:category_id>/', views.post_list_by_category, name='post_list_by_category'),
    path('categories/', views.category_list, name='category_list'),  # 카테고리 목록
    path('categories/create/', views.category_create, name='category_create'),  # 카테고리 등록
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),  # 카테고리 수정
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]