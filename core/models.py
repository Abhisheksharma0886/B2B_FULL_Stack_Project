from django.db import models
from django.contrib.auth.models import AbstractUser
import random

class UserProfile(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('buyer', 'Buyer'),
        ('vendor', 'Vendor'),
        ('shipper', 'Shipped ID'),
        ('out_for_delivery', 'Out for Delivery ID'),
        ('delivered', 'Delivered ID'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='buyer')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    raw_password_view = models.CharField(max_length=128, blank=True, null=True)
    is_approved = models.BooleanField(default=True)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='employees_created')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Product(models.Model):
    vendor = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'role': 'vendor'}, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2) # In INR
    available_quantity = models.PositiveIntegerField(default=0)
    offer_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # 5 images as requested
    image1 = models.ImageField(upload_to='products/', blank=True, null=True)
    image2 = models.ImageField(upload_to='products/', blank=True, null=True)
    image3 = models.ImageField(upload_to='products/', blank=True, null=True)
    image4 = models.ImageField(upload_to='products/', blank=True, null=True)
    image5 = models.ImageField(upload_to='products/', blank=True, null=True)

    @property
    def discounted_price(self):
        discount = (self.price * self.offer_percentage) / 100
        return round(self.price - discount, 2)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Order Confirmed'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    buyer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'role': 'buyer'}, related_name='buyer_orders')
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50, default='Cash on Delivery')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='confirmed')
    otp = models.CharField(max_length=6, blank=True)

    # Supply Chain Tracking timestamps
    order_confirmed_at = models.DateTimeField(auto_now_add=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    out_for_delivery_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.otp:
            # Generate 6-digit OTP
            self.otp = "".join([str(random.randint(0, 9)) for _ in range(6)])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} - {self.product.name} ({self.status})"
