from django.urls import path
from . import views



urlpatterns = [
    path('', views.home_page, name='home-page'),
    path('about-us/', views.about_us_page, name='about_us_page'),
    path('products/', views.product_listing, name='product_listing'),
    # path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    path('blogs/', views.blog_list, name='blog_list'),
    path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/add/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('place-order/', views.place_order, name='place_order'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('orders/', views.order_history_view, name='orders'),
    path('addresses/', views.addresses_view, name='addresses'),
    path('cards/', views.payment_cards_view, name='payment_cards'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('myaccount/', views.home_view, name='home_view'),
    path('toggle/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/add-all/', views.add_all_to_cart, name='add_all_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),


]