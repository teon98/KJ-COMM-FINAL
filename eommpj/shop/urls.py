from django.urls import path
from . import views  # 현재 디렉토리의 views를 가져옵니다

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.main_home, name='main_home'),  # 기본 페이지 경로
    path('accounts-info/', views.accounts_info, name="accounts_info"),
    path('upload-category/', views.category_upload, name='upload_category'),
    path('upload-category/<int:id>/', views.category_edit, name='category_edit'),  # 수정 동작
    path('delete-category/<int:category_id>/', views.delete_category, name='delete_category'),
]

# 미디어 파일 서빙 설정
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)