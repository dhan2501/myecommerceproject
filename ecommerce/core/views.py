from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from dashboard.models import ProductCategory, Product, Coupon, Order, OrderItem, HomeSlider, HomeFeature, ProductReview, Blog, Wishlist, Cart
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import login


# django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ShippingAddressForm, PaymentCardForm
from .models import ShippingAddress, PaymentCard
from dashboard.models import Order, CustomerReview # assuming this is where orders live
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import ProductReviewForm
from django.contrib.auth import logout

def home_page(request):
    sliders = HomeSlider.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True).order_by('-created_at')  # or any filter
    features = HomeFeature.objects.all()
    customer_reviews = CustomerReview.objects.all().order_by('-created_at')[:10]
    categories = ProductCategory.objects.filter(is_active=True)
    blogs = Blog.objects.filter(status='published').order_by('-created_at')
    
    # Get product IDs in wishlist for the logged-in user
    wishlist_product_ids = []
    if request.user.is_authenticated:
        wishlist_product_ids = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)

    params= {'products': products, 
             'sliders': sliders, 
             'features': features, 
             'customer_reviews' : customer_reviews,
             'categories' : categories,
             'blogs' : blogs,
             'wishlist_product_ids' : wishlist_product_ids
            }
    return render(request, 'home.html', params)

def about_us_page(request):
    return render(request, 'about.html')

def product_listing(request):
    category_slug = request.GET.get('category')
    products = Product.objects.all()

    if category_slug:
        category = get_object_or_404(ProductCategory, slug=category_slug)
        products = products.filter(category=category)

    context = {
        'products': products,
        'categories': ProductCategory.objects.all(),  # if you're showing category list
    }
    return render(request, 'product_listing.html', context)


    context = {
        'categories': categories,
        'products': products,
        # 'cart_count': cart_count,
        'selected_category': int(category_filter) if category_filter else None
    }
    return render(request, 'product_listing.html', context)

@require_POST
def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)
    quantity = int(request.POST.get('quantity', 1))
    cart = request.session.get('cart', {})

    product_id_str = str(id)
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += quantity
    else:
        cart[product_id_str] = {
            'quantity': quantity,
            'price': float(product.sale_price or product.regular_price),
            'title': product.title
        }

    request.session['cart'] = cart
    return redirect(request.META.get('HTTP_REFERER', 'product_listing'))

def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id_str, item in cart.items():
        try:
            product = Product.objects.get(id=int(product_id_str))
            quantity = item.get('quantity', 1)
            price = product.sale_price or product.regular_price
            total = quantity * price
            total_price += total

            cart_items.append({
                'product': product,
                'quantity': quantity,
                'price': price,
                'total': total,
                'subtotal': total,
                'image': product.image.url if product.image else ''
            })

        except Product.DoesNotExist:
            continue

    return render(request, 'cart_detail.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.order_by('-created_at')  # Assumes related_name='reviews' in ProductReview

    # Review form logic
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.save()
            return redirect('product_detail', slug=product.slug)
    else:
        form = ProductReviewForm()

    # Cart count logic
    cart = request.session.get('cart', {})
    cart_count = sum(item['quantity'] if isinstance(item, dict) else item for item in cart.values())

    context = {
        'product': product,
        'cart_count': cart_count,
        'reviews': reviews,
        'form': form
    }
    return render(request, 'product_detail.html', context)

# Apply coupon view
def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            request.session['applied_coupon'] = {
                'code': coupon.code,
                'discount_amount': coupon.discount_amount
            }
            messages.success(request, f"Coupon '{coupon.code}' applied successfully! Discount: ₹{coupon.discount_amount}")
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid or expired coupon code.")
    
    return redirect('cart_detail')


# Checkout page
def checkout(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id, item in cart.items():
        product = get_object_or_404(Product, id=product_id)
        quantity = item['quantity'] if isinstance(item, dict) else item
        price = float(item.get('price', product.sale_price or product.regular_price)) if isinstance(item, dict) else (product.sale_price or product.regular_price)
        subtotal = quantity * price
        total_price += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'price': price,
            'subtotal': subtotal,
            'total': subtotal
        })

    # Apply coupon if exists
    applied_coupon = request.session.get('applied_coupon')
    discount_amount = 0
    if applied_coupon:
        discount_amount = applied_coupon.get('discount_amount', 0)
        total_price -= discount_amount

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'discount_amount': discount_amount,
        'applied_coupon': applied_coupon
    }
    return render(request, 'checkout.html', context)

def place_order(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postcode = request.POST.get('postcode')
        total_price = request.POST.get('total_price')

        # Save Order
        order = Order.objects.create(
            customer=request.user,  # <-- This is necessary
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            postcode=postcode,
            total_price=total_price
        )

        # Save Order Items
        cart = request.session.get('cart', {})

        for product_id, item in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                OrderItem.objects.create(
                    order=order,
                    product_name=product.title,
                    price=item['price'],
                    quantity=item['quantity']
                )
            except Product.DoesNotExist:
                pass

        # Clear cart and coupon
        request.session['cart'] = {}
        if 'applied_coupon' in request.session:
            del request.session['applied_coupon']

        
        messages.success(request, f"Thank you {full_name}, your order has been placed!")

        return redirect('product_listing')
    else:
        return HttpResponse("Invalid Request")
    

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart

    cart_count = sum(item['quantity'] for item in cart.values())

    return JsonResponse({'success': True, 'cart_count': cart_count})




# Register View
def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful.")
            return redirect('login')  # Redirect to login page
    else:
        form = CustomUserCreationForm()
    return render(request, 'myaccount/register.html', {'form': form})

# Login View
def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('product_listing')  # Redirect to home page after login
    else:
        form = CustomAuthenticationForm()
    return render(request, 'myaccount/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'myaccount/order_detail.html', {'order': order})


@login_required
def order_history_view(request):
    # orders = Order.objects.filter(user=request.user)
    orders = Order.objects.filter(email=request.user.email).order_by('-created_at')
    return render(request, 'myaccount/order_history.html', {'orders': orders})

@login_required
def addresses_view(request):
    addresses = ShippingAddress.objects.filter(user=request.user)
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('addresses')
    else:
        form = ShippingAddressForm()
    return render(request, 'myaccount/addresses.html', {'form': form, 'addresses': addresses})

@login_required
def payment_cards_view(request):
    cards = PaymentCard.objects.filter(user=request.user)
    if request.method == 'POST':
        form = PaymentCardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user
            card.save()
            return redirect('payment_cards')
    else:
        form = PaymentCardForm()
    return render(request, 'myaccount/payment_cards.html', {'form': form, 'cards': cards})

def logout_view(request):
    logout(request)
    return redirect('login')


# Home page view
def home_view(request):
    return render(request, 'myaccount/home.html')

def category_detail(request, pk):
    category = get_object_or_404(ProductCategory, is_active=True, pk=pk)
    products = Product.objects.filter(category=category)
    return render(request, 'category_detail.html', {
        'category': category,
        'products': products
    })

def blog_list(request):
    blogs = Blog.objects.filter(status='published').order_by('-created_at')
    return render(request, 'blog_list.html', {'blogs': blogs})

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug, status='published')
    return render(request, 'blog/blog_detail.html', {'blog': blog})

@login_required
def toggle_wishlist(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if not created:
            wishlist_item.delete()
            return JsonResponse({'status': 'removed'})
        return JsonResponse({'status': 'added'})
    

@login_required
def add_all_to_cart(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    
    for item in wishlist_items:
        # Example logic for adding to cart (update to match your Cart model structure)
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=item.product,
            defaults={'quantity': 1}  # Adjust as needed
        )
        if not created:
            cart_item.quantity += 1
            cart_item.save()

    # Optionally clear wishlist after adding to cart
    wishlist_items.delete()
    messages.success(request, "All wishlist items added to cart.")
    return redirect('view_cart')


@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart/view_cart.html', context)

def add_to_wishlist(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')

    product = get_object_or_404(Product, id=product_id)

    # Add to cart logic (update this depending on your Cart model)
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # Optionally remove from wishlist
    Wishlist.objects.filter(user=request.user, product=product).delete()

    return redirect('view_cart')  # or wherever you want to go

@login_required
def remove_from_wishlist(request, product_id):
    if request.method == "POST":
        Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect(request.META.get('HTTP_REFERER', 'home'))

