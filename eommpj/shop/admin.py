from django.contrib import admin
from .models import Category, Product
# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'image')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'price', 'is_free_shipping', 'is_admin_recommended']