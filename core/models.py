from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta



class Product(models.Model):

    CATEGORY_CHOICES = [
        ('phone', 'Smartphone'),
        ('laptop', 'Laptop'),
        ('camera', 'Camera'),
        ('audio', 'Audio'),
        ('watch', 'Smartwatch'),
        ('tablet', 'Tablet'),
        ('accessories', 'Accessories'),
    ]

    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True
    )
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Order(models.Model):

    STATUS_CHOICES = [
    ('pending', 'Order Placed'),
    ('confirmed', 'Order Confirmed'),
    ('packed', 'Packed'),
    ('shipped', 'Shipped'),
    ('out_for_delivery', 'Out for Delivery'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    full_name = models.CharField(max_length=150)

    phone = models.CharField(max_length=15)

    address = models.TextField()

    city = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    pincode = models.CharField(max_length=10)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('upi', 'UPI'),
        ('card', 'Credit/Debit Card'),
        ('netbanking', 'Net Banking'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cod'
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )

    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"




class EmailVerificationOTP(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='email_otp'
    )

    otp = models.CharField(max_length=6)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"{self.user.username} - OTP"
    
    
    
    
class Wishlist(models.Model):

 user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

 product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

created_at = models.DateTimeField(auto_now_add=True)

class Meta:
        unique_together = ('user', 'product')

def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    
    
    
class Review(models.Model):

    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    rating = models.IntegerField(
        choices=RATING_CHOICES
    )

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating} Stars"
    
    
    

class SavedAddress(models.Model):

    ADDRESS_TYPES = [
        ('home', 'Home'),
        ('office', 'Office'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_addresses'
    )

    address_type = models.CharField(
        max_length=20,
        choices=ADDRESS_TYPES,
        default='home'
    )

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.address_type}"
    
    
    
    
    