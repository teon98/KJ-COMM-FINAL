from django.contrib import admin
from .models import Category, Product, Order
# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'image')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'price', 'is_free_shipping', 'is_admin_recommended']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'total_price', 'payment_method', 'payment_status', 'order_date')
    list_filter = ('payment_status', 'payment_method', 'order_date')
    search_fields = ('user__username', 'cart_group_id')