from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Q
from .models import Category, Product, Cart, CartItem, Order, OrderItem
from .forms import CheckoutForm
import stripe
import json
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY

class HomeView(TemplateView):
    template_name = 'store/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()[:3]
        context['featured_products'] = Product.objects.filter(available=True)[:8]
        return context

class ProductListView(ListView):
    model = Product
    template_name = 'store/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(available=True)
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)

        # Price filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Sorting
        sort = self.request.GET.get('sort')
        if sort:
            if sort.startswith('-'):
                queryset = queryset.order_by(sort)
            else:
                queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = None
        if self.kwargs.get('category_slug'):
            context['current_category'] = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return context

class CategoryProductsView(ProductListView):
    def get_queryset(self):
        return super().get_queryset().filter(
            category__slug=self.kwargs['slug']
        )

class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = Product.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id)[:4]
        return context

class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'store/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        cart_items = cart.items.all()
        
        # Calculate totals using Decimal
        subtotal = sum(item.total_price for item in cart_items)
        shipping = Decimal('10.00') if subtotal > 0 else Decimal('0.00')
        tax = subtotal * Decimal('0.10')  # 10% tax
        total = subtotal + shipping + tax
        
        context.update({
            'cart': cart,
            'cart_items': cart_items,
            'subtotal': subtotal,
            'shipping': shipping,
            'tax': tax,
            'total': total
        })
        return context

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart.')
    return redirect('store:cart')

@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
            
            cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
            cart_item.quantity = quantity
            cart_item.save()
            
            # Calculate cart totals using Decimal
            cart = cart_item.cart
            subtotal = sum(item.total_price for item in cart.items.all())
            shipping = Decimal('10.00') if subtotal > 0 else Decimal('0.00')
            tax = subtotal * Decimal('0.10')
            total = subtotal + shipping + tax
            
            return JsonResponse({
                'success': True,
                'message': 'Cart updated successfully',
                'item_total': str(cart_item.total_price),
                'cart_total': str(total)
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)

@login_required
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        try:
            cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
            cart = cart_item.cart
            cart_item.delete()
            
            # Calculate cart totals using Decimal
            subtotal = sum(item.total_price for item in cart.items.all())
            shipping = Decimal('10.00') if subtotal > 0 else Decimal('0.00')
            tax = subtotal * Decimal('0.10')
            total = subtotal + shipping + tax
            
            return JsonResponse({
                'success': True,
                'message': 'Item removed from cart successfully',
                'cart_total': str(total)
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)

class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'store/checkout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        cart_items = cart.items.all()
        
        # Calculate totals using Decimal
        subtotal = sum(item.total_price for item in cart_items)
        shipping = Decimal('10.00') if subtotal > 0 else Decimal('0.00')
        tax = subtotal * Decimal('0.10')  # 10% tax
        total = subtotal + shipping + tax
        
        context.update({
            'cart': cart,
            'cart_items': cart_items,
            'subtotal': subtotal,
            'shipping': shipping,
            'tax': tax,
            'total': total,
            'form': CheckoutForm(),
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY
        })
        return context

    def post(self, request, *args, **kwargs):
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                # Calculate total price including tax and shipping
                cart = request.user.cart
                cart_items = cart.items.all()
                subtotal = sum(item.total_price for item in cart_items)
                shipping = Decimal('10.00') if subtotal > 0 else Decimal('0.00')
                tax = subtotal * Decimal('0.10')
                total = subtotal + shipping + tax

                # Create payment intent
                intent = stripe.PaymentIntent.create(
                    amount=int(total * 100),  # Convert to cents
                    currency='usd',
                    payment_method=request.POST.get('payment_method_id'),
                    confirm=True,
                )

                # Create order
                order = Order.objects.create(
                    user=request.user,
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['email'],
                    phone=form.cleaned_data['phone'],
                    address=form.cleaned_data['address'],
                    city=form.cleaned_data['city'],
                    state=form.cleaned_data['state'],
                    zip_code=form.cleaned_data['zip_code'],
                    total_price=total,
                    stripe_payment_intent=intent.id
                )

                # Create order items
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        price=item.product.price,
                        quantity=item.quantity
                    )

                # Clear cart
                cart_items.delete()
                messages.success(request, 'Order placed successfully!')
                return redirect('store:payment_success')

            except stripe.error.CardError as e:
                messages.error(request, f'Payment failed: {e.error.message}')
            except Exception as e:
                messages.error(request, 'An error occurred. Please try again.')
        
        return self.get(request, *args, **kwargs)

class PaymentView(LoginRequiredMixin, TemplateView):
    template_name = 'store/payment.html'

    def post(self, request, *args, **kwargs):
        cart = Cart.objects.get(user=request.user)
        total = int(cart.get_total_price() * 100)  # Convert to cents for Stripe

        try:
            intent = stripe.PaymentIntent.create(
                amount=total,
                currency='usd',
                metadata={'user_id': request.user.id}
            )
            return JsonResponse({
                'clientSecret': intent.client_secret
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=403)

class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'store/payment_success.html'

    def get(self, request, *args, **kwargs):
        cart = Cart.objects.get(user=request.user)
        order = Order.objects.create(
            user=request.user,
            total_price=cart.get_total_price()
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )

        cart.items.all().delete()
        return super().get(request, *args, **kwargs)

class PaymentCancelView(LoginRequiredMixin, TemplateView):
    template_name = 'store/payment_cancel.html'

def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': str(e)}, status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        user_id = payment_intent['metadata']['user_id']
        # Handle successful payment (e.g., update order status)

    return JsonResponse({'status': 'success'})
