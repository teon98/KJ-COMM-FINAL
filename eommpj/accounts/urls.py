from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from .views import CustomLoginView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('register_form/', views.register_form, name="register_form"),
    path('check-userid/', views.check_userid, name='check_userid'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('update-user-role/<int:user_id>/', views.update_user_role, name='update_user_role'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('password-find/', views.password_find_form, name='password_find'),
    path('password-find/<str:email>/', views.password_find_process, name='password_find_with_email'),
    path('customlogin/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='customlogin'),
]
