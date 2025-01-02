from django.urls import path
from . import views  # 현재 디렉토리의 views를 가져옵니다

urlpatterns = [
    # path('', views.main_home, name='main_home'),  # 기본 페이지 경로
    path('post/', views.PostList.as_view(), name='post_list'),
    path('post/<int:pk>/', views.PostDetail.as_view(), name ='post_detail'),
    path('create_post/', views.PostCreate.as_view(), name ='create_post'),
    path('delete_post/<int:pk>/', views.PostDelete.as_view(), name='delete_post'),
    path('update_post/<int:pk>/', views.PostUpdate.as_view(), name='update_post'),
    path('blog/', views.BLogList.as_view(), name='blog_list'),
    path('blog/<int:pk>/', views.BlogDetail.as_view(), name ='blog_detail'),
    path('create_blog/', views.BlogCreate.as_view(), name ='create_blog'),
    path('delete_blog/<int:pk>/', views.BlogDelete.as_view(), name='delete_blog'),
    path('update_blog/<int:pk>/', views.BlogUpdate.as_view(), name='update_blog'),
    path('accounts-info/', views.accounts_info, name="accounts_info")
]

# urlpatterns = format_suffix_patterns(url)