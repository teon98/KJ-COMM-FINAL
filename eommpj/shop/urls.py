from django.urls import path
from . import views  # 현재 디렉토리의 views를 가져옵니다

urlpatterns = [
    path('', views.home, name='home'),  # 기본 페이지 경로
]