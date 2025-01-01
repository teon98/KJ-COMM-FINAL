from django.urls import path
from . import views  # 현재 디렉토리의 views를 가져옵니다

urlpatterns = [
    # path('', views.main_home, name='main_home'),  # 기본 페이지 경로
    path('', views.PostList.as_view()),
    path('<int:pk>/', views.PostDetail.as_view()),
    path('create_post/', views.PostCreate.as_view()),
]

# urlpatterns = format_suffix_patterns(url)