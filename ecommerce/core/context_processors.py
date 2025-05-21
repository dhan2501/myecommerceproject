from dashboard.models import Product

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