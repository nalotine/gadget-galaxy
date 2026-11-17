from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q
import random
from .models import Product, Order, OrderItem, EmailVerificationOTP, Wishlist, Review
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import SavedAddress
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import reverse
import json
from django.views.decorators.http import require_POST
from .ai_service import ask_gemini






def home(request):
    products = Product.objects.filter(is_available=True)

    context = {
        'products': products
    }

    return render(request, 'home.html', context)


def search_products(request):
    query = request.GET.get('q', '')

    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(brand__icontains=query),
        is_available=True
    )

    return render(request, 'search_results.html', {
        'products': products,
        'query': query
    })



#product detail view--------------------->

def product_detail(request, id):
    product = get_object_or_404(
        Product,
        id=id,
        is_available=True
    )

    context = {
        'product': product
    }

    return render(request, 'product_detail.html', context)



#cart views--------------------->
def add_to_cart(request, id):
    product = get_object_or_404(
        Product,
        id=id,
        is_available=True
    )

    cart = request.session.get('cart', {})

    product_id = str(product.id)

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')
def cart(request):
    cart_data = request.session.get('cart', {})

    cart_items = []
    total = 0

    for product_id, quantity in cart_data.items():

        product = get_object_or_404(
            Product,
            id=product_id
        )

        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    context = {
        'cart_items': cart_items,
        'total': total,
    }

    return render(request, 'cart.html', context)



def update_cart(request, id):
    product = get_object_or_404(
        Product,
        id=id,
        is_available=True
    )

    cart = request.session.get('cart', {})

    product_id = str(product.id)

    action = request.GET.get('action')

    current_quantity = cart.get(product_id, 0)

    if action == 'increase':

        if current_quantity < product.stock:
            cart[product_id] = current_quantity + 1

    elif action == 'decrease':

        if current_quantity > 1:
            cart[product_id] = current_quantity - 1

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


def remove_from_cart(request, id):

    cart = request.session.get('cart', {})

    product_id = str(id)

    if product_id in cart:
        del cart[product_id]

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


#registration and login views--------------------->

def register(request):

    if request.method == 'POST':

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        terms = request.POST.get('terms')

        # Check terms and conditions
        if not terms:
            return render(request, 'register.html', {
                'error': 'You must agree to the Terms and Conditions.'
            })

        # Check password
        if password != confirm_password:
            return render(request, 'register.html', {
                'error': 'Passwords do not match.'
            })

        # Check username
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {
                'error': 'Username already exists.'
            })

        # Check email
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {
                'error': 'Email already registered.'
            })

        # Create inactive user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        user.is_active = False
        user.save()

        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # Save OTP
        EmailVerificationOTP.objects.create(
            user=user,
            otp=otp
        )

        # Send OTP email
        send_mail(
            subject='Your Gadget Galaxy verification OTP',
            message=f'''
Hello {first_name} {last_name},

Thank you for registering with Gadget Galaxy.

Your email verification OTP is:

{otp}

This OTP is valid for 10 minutes.

If you did not create this account, you can ignore this email.

Regards,
Gadget Galaxy
''',
            from_email=None,
            recipient_list=[email],
            fail_silently=False
        )

        # Open OTP verification page
        return redirect(
            'verify_otp',
            username=user.username
        )

    return render(request, 'register.html')



def verify_otp(request, username):

    user = get_object_or_404(
        User,
        username=username
    )

    otp_record = EmailVerificationOTP.objects.filter(
        user=user
    ).first()

    if not otp_record:
        return render(request, 'verify_otp.html', {
            'error': 'No verification OTP found.'
        })

    if request.method == 'POST':

        entered_otp = request.POST.get('otp')

        if otp_record.is_expired():

            otp_record.delete()

            return render(request, 'verify_otp.html', {
                'error': 'OTP has expired. Please register again.'
            })

        if entered_otp == otp_record.otp:

            user.is_active = True
            user.save()

            otp_record.delete()

            return render(request, 'email_verified.html')

        return render(request, 'verify_otp.html', {
            'error': 'Invalid OTP. Please try again.',
            'username': username
        })

    return render(request, 'verify_otp.html', {
        'username': username
    })

   #login and logout views--------------------->

def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            if not user.is_active:
                return render(request, 'login.html', {
                    'error': 'Please verify your email before logging in.'
                })

            login(request, user)

            return redirect('home')

        return render(request, 'login.html', {
            'error': 'Invalid username or password.'
        })

    return render(request, 'login.html')




def logout_view(request):

    logout(request)

    return redirect('home')


#checkout and order views--------------------->
   

@login_required
def checkout(request):

    cart_data = request.session.get('cart', {})

    if not cart_data:
        return redirect('cart')

    cart_items = []
    total = 0

    for product_id, quantity in cart_data.items():

        product = get_object_or_404(
            Product,
            id=product_id,
            is_available=True
        )

        quantity = int(quantity)

        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    saved_addresses = SavedAddress.objects.filter(
        user=request.user
    ).order_by('-is_default', '-created_at')

    if request.method == 'POST':

        saved_address_id = request.POST.get('saved_address')

        # Use selected saved address
        if saved_address_id:

            saved_address = get_object_or_404(
                SavedAddress,
                id=saved_address_id,
                user=request.user
            )

            full_name = saved_address.full_name
            phone = saved_address.phone
            address = saved_address.address
            city = saved_address.city
            state = saved_address.state
            pincode = saved_address.pincode

        # Create order using the selected address
        else:

            return render(request, 'checkout.html', {
                'cart_items': cart_items,
                'total': total,
                'saved_addresses': saved_addresses,
                'error': 'Please select a saved address.'
            })

        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            full_name=full_name,
            phone=phone,
            address=address,
            city=city,
            state=state,
            pincode=pincode
        )

        for item in cart_items:

            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['product'].price
            )

        return redirect(
            'payment_method',
            order_id=order.id
        )

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'saved_addresses': saved_addresses,
    })



#payment method selection and processing views--------------------->

@login_required
def payment_method(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    if request.method == 'POST':

        selected_method = request.POST.get('payment_method')

        allowed_methods = [
            'cod',
            'upi',
            'card',
            'netbanking',
        ]

        if selected_method not in allowed_methods:
            return render(request, 'payment.html', {
                'order': order,
                'error': 'Please select a valid payment method.',
            })

        order.payment_method = selected_method
        order.payment_status = 'pending'
        order.save()

        if selected_method == 'cod':

             request.session['cart'] = {}
             request.session.modified = True

             return redirect('order_success', order_id=order.id)

        # Online payment will be connected in the next step.
        return render(request, 'payment.html', {
            'order': order,
            'selected_method': selected_method,
            'success': 'Payment option selected successfully. Please complete your payment.',
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        })

    return render(request, 'payment.html', {
        'order': order,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    })


@login_required
def order_success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(request, 'order_success.html', {
        'order': order
    })


def my_orders(request):

    if not request.user.is_authenticated:
        return redirect('login')

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, 'orders.html', {
        'orders': orders
    })
    
@login_required
def order_details(request, order_id):

    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        id=order_id,
        user=request.user
    )

    return render(request, 'order_details.html', {
        'order': order
    })
    
def add_to_wishlist(request, id):

    if not request.user.is_authenticated:
        return redirect('login')

    product = get_object_or_404(
        Product,
        id=id,
        is_available=True
    )

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect('wishlist')

def wishlist(request):

    if not request.user.is_authenticated:
        return redirect('login')

    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related('product')

    return render(request, 'wishlist.html', {
        'wishlist_items': wishlist_items
    })
    
    
    
 
def remove_from_wishlist(request, id):

    if not request.user.is_authenticated:
        return redirect('login')

    product = get_object_or_404(
        Product,
        id=id
    )

    Wishlist.objects.filter(
        user=request.user,
        product=product
    ).delete()

    return redirect('wishlist')   
    
    
    
def category_products(request, category):

    products = Product.objects.filter(
        category__iexact=category,
        is_available=True
    )

    # Sorting
    sort = request.GET.get('sort')

    if sort == 'price_low':
        products = products.order_by('price')

    elif sort == 'price_high':
        products = products.order_by('-price')

    elif sort == 'newest':
        products = products.order_by('-created_at')

    # In-stock filter
    stock = request.GET.get('stock')

    if stock == 'in_stock':
        products = products.filter(stock__gt=0)

    return render(request, 'category_products.html', {
        'products': products,
        'category': category
    })
    
    
def add_review(request, id):

    if not request.user.is_authenticated:
        return redirect('login')

    product = get_object_or_404(
        Product,
        id=id,
        is_available=True
    )

    if request.method == 'POST':

        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if rating and comment:

            Review.objects.update_or_create(
                user=request.user,
                product=product,
                defaults={
                    'rating': rating,
                    'comment': comment
                }
            )

    return redirect('product_detail', id=product.id)



def cancel_order(request, id):

    if not request.user.is_authenticated:
        return redirect('login')

    order = get_object_or_404(
        Order,
        id=id,
        user=request.user
    )

    # Only pending and confirmed orders can be cancelled
    if order.status not in ['pending', 'confirmed']:
        return redirect('my_orders')

    with transaction.atomic():

        # Restore product stock
        for item in order.items.all():

            item.product.stock += item.quantity
            item.product.save(update_fields=['stock'])

        # Change order status
        order.status = 'cancelled'
        order.save(update_fields=['status'])

    return redirect('my_orders')




@login_required
def my_account(request):
    user = request.user

    return render(request, 'my_account.html', {
        'account_user': user,
    })

#save addresses views--------------------->
@login_required
def saved_addresses(request):
    addresses = SavedAddress.objects.filter(
        user=request.user
    ).order_by('-is_default', '-created_at')

    return render(request, 'saved_addresses.html', {
        'addresses': addresses,
    })


@login_required
def edit_address(request, id):

    address = get_object_or_404(
        SavedAddress,
        id=id,
        user=request.user
    )

    if request.method == 'POST':

        address_type = request.POST.get('address_type', 'home')
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address_text = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        pincode = request.POST.get('pincode', '').strip()

        if not all([
            full_name,
            phone,
            address_text,
            city,
            state,
            pincode
        ]):

            return render(request, 'edit_address.html', {
                'address': address,
                'error': 'Please fill in all required fields.'
            })

        address.address_type = address_type
        address.full_name = full_name
        address.phone = phone
        address.address = address_text
        address.city = city
        address.state = state
        address.pincode = pincode

        address.save()

        return redirect('saved_addresses')

    return render(request, 'edit_address.html', {
        'address': address
    })


@login_required
def add_address(request):
    if request.method == 'POST':
        address_type = request.POST.get('address_type', 'home')
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        pincode = request.POST.get('pincode', '').strip()
        is_default = request.POST.get('is_default') == 'on'

        if not all([full_name, phone, address, city, state, pincode]):
            return render(request, 'add_address.html', {
                'error': 'Please fill in all required fields.'
            })

        if is_default:
            SavedAddress.objects.filter(
                user=request.user
            ).update(is_default=False)

        SavedAddress.objects.create(
            user=request.user,
            address_type=address_type,
            full_name=full_name,
            phone=phone,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
            is_default=is_default,
        )

        return redirect('saved_addresses')

    return render(request, 'add_address.html')


client = razorpay.Client(
    auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    )
)







@login_required
def create_razorpay_order(request):
    if request.method != 'POST':
        return JsonResponse({
            'error': 'POST request required.'
        }, status=405)

    order_id = request.POST.get('order_id')

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    if order.payment_status == 'paid':
        return JsonResponse({
            'error': 'This order has already been paid.'
        }, status=400)

    amount = int(order.total_amount * 100)

    order_data = {
        'amount': amount,
        'currency': 'INR',
        'receipt': f'gadgetgalaxy_order_{order.id}',
    }

    razorpay_order = client.order.create(
        data=order_data
    )

    order.transaction_id = razorpay_order['id']
    order.payment_method = 'upi'
    order.payment_status = 'pending'
    order.save()

    return JsonResponse({
        'order_id': razorpay_order['id'],
        'amount': razorpay_order['amount'],
        'currency': razorpay_order['currency'],
    })





@login_required
def verify_razorpay_payment(request):

    if request.method != 'POST':
        return JsonResponse({
            'error': 'POST request required.'
        }, status=405)

    local_order_id = request.POST.get('local_order_id')
    razorpay_order_id = request.POST.get('razorpay_order_id')
    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    razorpay_signature = request.POST.get('razorpay_signature')

    if not all([
        local_order_id,
        razorpay_order_id,
        razorpay_payment_id,
        razorpay_signature
    ]):
        return JsonResponse({
            'error': 'Payment information is incomplete.'
        }, status=400)

    order = get_object_or_404(
        Order,
        id=local_order_id,
        user=request.user
    )

    # Confirm this gateway order belongs to our Django order.
    if order.transaction_id != razorpay_order_id:
        return JsonResponse({
            'error': 'Razorpay order does not match.'
        }, status=400)

    # Verify Razorpay's payment signature.
    params = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_signature': razorpay_signature,
    }

    try:
        client.utility.verify_payment_signature(params)

    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({
            'error': 'Payment signature verification failed.'
        }, status=400)

    # Only after successful signature verification:
    order.payment_status = 'paid'
    order.transaction_id = razorpay_payment_id
    order.save(update_fields=[
        'payment_status',
        'transaction_id'
    ])

   # Clear cart after successful payment
    request.session['cart'] = {}
    request.session.modified = True

    return JsonResponse({
    'success': True,
    'message': 'Payment successful!',
    'order_id': order.id,
    'redirect_url': reverse(
        'order_success',
        kwargs={'order_id': order.id}
    ),
})


@login_required
def make_default_address(request, id):

    if request.method == 'POST':

        address = get_object_or_404(
            SavedAddress,
            id=id,
            user=request.user
        )

        # Remove default status from all saved addresses
        SavedAddress.objects.filter(
            user=request.user
        ).update(is_default=False)

        # Make selected address the default
        address.is_default = True
        address.save()

    return redirect('saved_addresses')


@login_required
def track_order(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    tracking_steps = [
        ('pending', 'Order Placed'),
        ('confirmed', 'Order Confirmed'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
    ]

    current_status = order.status

    return render(request, 'track_order.html', {
        'order': order,
        'tracking_steps': tracking_steps,
        'current_status': current_status,
    })
    
    
@require_POST
def ai_chat(request):

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({
                'reply': 'Please enter a message.'
            }, status=400)

        reply = ask_gemini(user_message, request.user)

        return JsonResponse({
            'reply': reply
        })

    except Exception as e:
        return JsonResponse({
            'reply': 'Sorry! Our AI assistant is temporarily unavailable.'
        }, status=500)
        
        
@login_required
def ai_chat_page(request):
    return render(request, 'ai_chat.html')