from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    path('product/<int:id>/', views.product_detail, name='product_detail'),
    
    path('cart/add/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('cart/update/<int:id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.my_orders, name='my_orders'),
    path('verify-otp/<str:username>/', views.verify_otp, name='verify_otp'),
    path('wishlist/add/<int:id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    path('wishlist/', views.wishlist, name='wishlist'),
    path('search/', views.search_products, name='search_products'),
    path('category/<str:category>/', views.category_products, name='category_products'),

    path('add-review/<int:id>/', views.add_review, name='add_review'),
    path('cancel-order/<int:id>/', views.cancel_order, name='cancel_order'),
    
    path('payment/<int:order_id>/', views.payment_method, name='payment_method'),

    path('my-account/', views.my_account, name='my_account'),
    
    path('saved-addresses/', views.saved_addresses,name='saved_addresses'),
    
    path('add-address/',views.add_address,name='add_address'),
    
    path('create-razorpay-order/',views.create_razorpay_order,name='create_razorpay_order'),
    
    
    path('verify-razorpay-payment/',views.verify_razorpay_payment,name='verify_razorpay_payment'),

    
    path('saved-addresses/edit/<int:id>/',views.edit_address,name='edit_address'),

    
    path('saved-addresses/default/<int:id>/',views.make_default_address,name='make_default_address'),
    path('track-order/<int:order_id>/',views.track_order,name='track_order'),
    
    path('order-success/<int:order_id>/',views.order_success,name='order_success'),
    path('order-details/<int:order_id>/',views.order_details,name='order_details'),
    path('ai-chat/', views.ai_chat, name='ai_chat'),
    path('ai-assistant/',views.ai_chat_page,name='ai_chat_page'),




]   


