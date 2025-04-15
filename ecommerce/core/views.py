from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from dashboard.models import ProductCategory, Product, Coupon, Order, OrderItem
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST


def product_listing(request):
    # Fetch all categories for the sidebar/filter
    categories = ProductCategory.objects.all()

    # Start with all products
    products = Product.objects.all()

    # Apply category filter if provided via GET
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category_id=category_filter)


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
        product = get_object_or_404(Product, id=int(product_id_str))
        quantity = item['quantity']
        price = item['price']
        subtotal = quantity * price
        total_price += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'price': price,
            'subtotal': subtotal
        })

    return render(request, 'cart_detail.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


# Product detail page
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    cart = request.session.get('cart', {})
    cart_count = sum(item['quantity'] if isinstance(item, dict) else item for item in cart.values())

    context = {
        'product': product,
        'cart_count': cart_count
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
            'subtotal': subtotal
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

        from django.contrib import messages
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