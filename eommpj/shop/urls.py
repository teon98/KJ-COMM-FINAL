from django.urls import path
from . import views  # 현재 디렉토리의 views를 가져옵니다

from django.conf import settings
from django.conf.urls.static import static
from .views import product_upload, get_child_categories
from django.urls import re_path

urlpatterns = [
    path('', views.main_home, name='main_home'),  # 기본 페이지 경로
    path('accounts-info/', views.accounts_info, name="accounts_info"),
    path('upload-category/', views.category_upload, name='upload_category'),
    path('upload-category/<int:id>/', views.category_edit, name='category_edit'),  # 수정 동작
    path('delete-category/<int:category_id>/', views.delete_category, name='delete_category'),
    # 키 값이 없는 경우: 전체 상품을 보여줌
    path('category/', views.category_detail, name='all_products'),
    # 키 값이 있는 경우: 특정 카테고리의 상품을 보여줌
    re_path(r'^category/(?P<category_name>.+)/$', views.category_detail, name='category_detail'),
    path('setting/', views.setting, name="setting"), #관리자 설정
    path('upload-product', product_upload, name="upload_product"),
    path('products/', views.product_list, name='product_list'),
    path('api/categories/<int:parent_id>/', get_child_categories, name='get_child_categories'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('my-page/', views.my_page, name='my_page'),
    path('company_introduce', views.company_introduce, name="company_introduce"),
    path('use_info', views.use_info, name="use_info"),
    path('usage_policy', views.usage_policy, name="usage_policy"),
    path('product/search/', views.product_search, name='product_search'),
    path('payment_option/<int:product_id>/', views.payment_option, name='payment_option'),
    path('admin/orders/', views.admin_order_list, name='admin_order_list'),
    path('admin/orders/<int:order_id>/update/', views.update_payment_status, name='update_payment_status'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='cart_add'),
    path('cart/remove/<int:cart_item_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:cart_item_id>/', views.update_cart, name='cart_update'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path(' /', views.checkout, name='checkout'),
    path('buy_now/<int:product_id>', views.buy_now, name='buy_now'),
    path('checkout/complete/<str:cart_group_id>/', views.checkout_complete, name='checkout_complete'),
    path('orders/', views.my_orders, name='my_orders'),
    path('checkout/bank-transfer/<str:cart_group_id>/', views.bank_transfer_guide, name='bank_transfer_guide'),
    path('admin/orders/<str:cart_group_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('payment/<uuid:cart_group_id>/', views.payment_view, name='payment_view'),
    path('checkout/complete/<str:cart_group_id>/', views.checkout_complete, name='checkout_complete'),
    path('my_orders', views.my_orders, name='my_orders'),
]

# 미디어 파일 서빙 설정
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)