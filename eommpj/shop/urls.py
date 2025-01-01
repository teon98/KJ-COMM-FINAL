from django.urls import path
from . import views  # 현재 디렉토리의 views를 가져옵니다

urlpatterns = [
    # path('', views.main_home, name='main_home'),  # 기본 페이지 경로
    path('post/', views.PostList.as_view(), name='post_list'),
    path('post/<int:pk>/', views.PostDetail.as_view(), name ='post_detail'),
    path('create_post/', views.PostCreate.as_view(), name ='create_post'),
    path('delete_post/<int:pk>/', views.PostDelete.as_view(), name='post_delete'),
    path('update_post/<int:pk>/', views.PostUpdate.as_view(), name='post_edit'),
]

# urlpatterns = format_suffix_patterns(url)