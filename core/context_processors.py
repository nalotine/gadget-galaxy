from .models import Wishlist


def wishlist_count(request):

    if request.user.is_authenticated:

        count = Wishlist.objects.filter(
            user=request.user
        ).count()

    else:

        count = 0

    return {
        'wishlist_count': count
    }


def cart_count(request):

    cart = request.session.get('cart', {})

    count = 0

    for quantity in cart.values():
        count += quantity

    return {
        'cart_count': count
    }