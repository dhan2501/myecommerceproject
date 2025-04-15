from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_listing, name='product_listing'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/add/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('place-order/', views.place_order, name='place_order'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),


]