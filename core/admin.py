
from django.contrib import admin
from .models import Product, Order, OrderItem, Wishlist, Review


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'brand',
        'category',
        'price',
        'stock',
        'is_available',
        'created_at'
    )

    list_filter = (
        'category',
        'brand',
        'is_available'
    )

    search_fields = (
        'name',
        'brand'
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'full_name',
        'phone',
        'total_amount',
        'status',
        'payment_status',
        'created_at'
    )

    list_filter = (
        'status',
        'payment_status',
        'created_at'
    )

    search_fields = (
        'id',
        'full_name',
        'phone',
        'user__username'
    )

    list_editable = (
        'status',
    )

    ordering = ('-created_at',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        'order',
        'product',
        'quantity',
        'price'
    )

    search_fields = (
        'product__name',
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'product',
        'rating',
        'created_at',
    )

    list_filter = (
        'rating',
        'created_at',
    )

    search_fields = (
        'user__username',
        'product__name',
        'comment',
    )

    ordering = ('-created_at',)
