# admin.py
from django.contrib import admin
from .models import ProductCategory, Product, ProductTag, Order, OrderItem, Coupon

from django.utils.html import format_html

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_display', 'is_active', 'created_at')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'image_display')
    search_fields = ('name', 'description', 'meta_title')
    list_filter = ('is_active', 'created_at')

    def image_display(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="70" height="auto" />', obj.image.url)
        return "No Image"
    image_display.short_description = 'Category Image'


# ProductTag Admin
@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name',)
    ordering = ('-created_at',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_display', 'regular_price', 'sale_price', 'discount_percentage', 'is_active', 'created_at')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'image_display', 'discount_percentage')
    search_fields = ('title', 'description', 'meta_title')
    list_filter = ('category', 'tags', 'is_active', 'created_at')

    def image_display(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="70" height="auto" />', obj.image.url)
        return "No Image"
    image_display.short_description = 'Product Image'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'total_price', 'created_at')
    list_filter = ('created_at', 'city')
    search_fields = ('full_name', 'email', 'phone')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'price', 'quantity')
    search_fields = ('product_name',)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_amount', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('code',)