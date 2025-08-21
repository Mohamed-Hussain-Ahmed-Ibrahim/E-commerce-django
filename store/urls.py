from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('category/<slug:slug>/', views.CategoryProductsView.as_view(), name='category_products'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('payment/', views.PaymentView.as_view(), name='payment'),
    path('payment/success/', views.PaymentSuccessView.as_view(), name='payment_success'),
    path('payment/cancel/', views.PaymentCancelView.as_view(), name='payment_cancel'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
] 