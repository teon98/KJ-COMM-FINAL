"""
URL configuration for eommpj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap
#from shop.models import YourModel  # 사이트의 주요 모델
from django.contrib import admin
from django.urls import path, include
from shop import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

# class YourModelSitemap(Sitemap):
#     changefreq = "daily"  # 변경 빈도: daily, weekly 등
#     priority = 0.8  # 검색 엔진의 우선 순위 (0.1 ~ 1.0)

#     def items(self):
#         return YourModel.objects.all()  # 모든 객체를 사이트맵에 포함

#     def lastmod(self, obj):
#         return obj.updated_at  # 모델의 최종 수정 시간 필드

# sitemaps = {
#     'yourmodel': YourModelSitemap,
# }

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.main_home, name='main_home'),  # 기본 페이지
    path('shop/', include('shop.urls')),  # shop 앱 연결    
    path('accounts/', include('accounts.urls'), name='accounts'),  # 회원가입 경로 추가
    path('board/', include('board.urls')),
    #path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url='/password_reset/done/'
    ), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
     path('customlogin/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='customlogin'),  # 여기에 추가
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)