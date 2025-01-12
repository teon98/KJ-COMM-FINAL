from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('register_form/', views.register_form, name="register_form"),
    path('check-userid/', views.check_userid, name='check_userid'),
]
