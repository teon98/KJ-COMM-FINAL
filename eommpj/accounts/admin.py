from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('userid', 'email', 'user_type', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('userid', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'company', 'gender', 'birth_date', 'phone_number', 'mobile_number', 'address', 'homepage', 'recommender_id', 'additional_info')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('userid', 'email', 'password1', 'password2', 'is_staff', 'is_active', 'user_type')}
        ),
    )
    search_fields = ('userid', 'email')  # username 대신 userid 사용
    ordering = ('userid',)  # username 대신 userid 사용

admin.site.register(CustomUser, CustomUserAdmin)