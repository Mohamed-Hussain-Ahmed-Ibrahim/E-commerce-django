from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'available', 'created_at', 'updated_at')
    list_filter = ('available', 'created_at', 'updated_at', 'category')
    list_editable = ('price', 'stock', 'available')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'total_price', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('cart__user__username', 'product__name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'first_name', 'last_name')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'price', 'quantity', 'total_price')
    list_filter = ('order__status', 'product__category')
    search_fields = ('order__user__username', 'product__name')
