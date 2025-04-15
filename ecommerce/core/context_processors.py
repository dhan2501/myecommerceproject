def cart_counter(request):
    cart = request.session.get('cart', {})
    cart_count = sum(
        item['quantity'] if isinstance(item, dict) else item
        for item in cart.values()
    )
    return {
        'cart_count': cart_count
    }
