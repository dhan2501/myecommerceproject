from dashboard.models import Product, FooterContact, Wishlist

def cart_counter(request):
    cart = request.session.get('cart', {})
    cart_count = sum(
        item['quantity'] if isinstance(item, dict) else item
        for item in cart.values()
    )
    return {
        'cart_count': cart_count
    }




def cart_context(request):
    cart = request.session.get('cart', {})
    cart_items = []
    cart_total = 0

    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            quantity = item.get('quantity', 1)
            price = product.sale_price if product.sale_price is not None else product.regular_price or 0

            total = price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'price': price,
                'total': total,
                'image': product.image.url if product.image else ''
            })
            cart_total += total
        except Product.DoesNotExist:
            continue

    return {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }



def footer_contact_context(request):
    contact = FooterContact.objects.prefetch_related('emails', 'phones').first()
    return {'contact': contact}


def wishlist_context(request):
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user)
        wishlist_count = wishlist_items.count()
        wishlist_total_price = sum([
            item.product.sale_price or item.product.regular_price
            for item in wishlist_items
        ])
    else:
        wishlist_items = []
        wishlist_count = 0
        wishlist_total_price = 0

    return {
        'wishlist_items': wishlist_items,
        'wishlist_count': wishlist_count,
        'wishlist_total_price': wishlist_total_price,
    }