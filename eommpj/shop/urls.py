from django.urls import path
from . import views  # 현재 디렉토리의 views를 가져옵니다

from django.conf import settings
from django.conf.urls.static import static
from .views import product_upload, get_child_categories

urlpatterns = [
    path('', views.main_home, name='main_home'),  # 기본 페이지 경로
    path('accounts-info/', views.accounts_info, name="accounts_info"),
    path('upload-category/', views.category_upload, name='upload_category'),
    path('upload-category/<int:id>/', views.category_edit, name='category_edit'),  # 수정 동작
    path('delete-category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('category/<str:category_name>/', views.category_detail, name='category_detail'),
    path('setting/', views.setting, name="setting"), #관리자 설정
    path('upload-product', product_upload, name="upload_product"),
    path('products/', views.product_list, name='product_list'),
    path('api/categories/<int:parent_id>/', get_child_categories, name='get_child_categories'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),
]

# 미디어 파일 서빙 설정
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)