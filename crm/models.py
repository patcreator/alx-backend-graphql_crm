from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
import re

class Customer(models.Model):
    """Customer model extending Django's User for authentication"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__name']
    
    def clean(self):
        if self.phone:
            # Validate phone number format
            phone_pattern = r'^(\+\d{1,3}\d{6,14}|\d{3}-\d{3}-\d{4})$'
            if not re.match(phone_pattern, self.phone):
                raise ValidationError({'phone': 'Invalid phone number format. Use format: +1234567890 or 123-456-7890'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def name(self):
        return self.user.get_full_name() or self.user.username
    
    @property
    def email(self):
        return self.user.email
    
    def __str__(self):
        return f"{self.name} ({self.email})"

class Product(models.Model):
    """Product model with inventory tracking"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, 
                                validators=[MinValueValidator(0.01)])
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    low_stock_threshold = models.IntegerField(default=10, validators=[MinValueValidator(1)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    @property
    def is_low_stock(self):
        return self.stock < self.low_stock_threshold
    
    @property
    def is_out_of_stock(self):
        return self.stock == 0
    
    def __str__(self):
        return f"{self.name} - ${self.price} (Stock: {self.stock})"

class Order(models.Model):
    """Order model with status tracking"""
    
    # Order status choices
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'
        REFUNDED = 'refunded', 'Refunded'
    
    # Payment status choices
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'
    
    order_number = models.CharField(max_length=50, unique=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, through='OrderItem', related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_address = models.TextField()
    billing_address = models.TextField()
    order_date = models.DateTimeField(default=timezone.now)
    shipped_date = models.DateTimeField(blank=True, null=True)
    delivered_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-order_date']
    
    def generate_order_number(self):
        """Generate a unique order number"""
        import random
        import string
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"ORD-{timestamp}-{random_str}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Calculate order totals"""
        order_items = self.orderitem_set.all()
        self.subtotal = sum(item.total_price for item in order_items)
        self.total_amount = self.subtotal + self.tax - self.discount
        return self.total_amount
    
    def update_status(self, new_status):
        """Update order status with timestamp"""
        if new_status == self.Status.SHIPPED and not self.shipped_date:
            self.shipped_date = timezone.now()
        elif new_status == self.Status.DELIVERED and not self.delivered_date:
            self.delivered_date = timezone.now()
        
        self.status = new_status
        self.save()
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.customer.name} - ${self.total_amount}"

class OrderItem(models.Model):
    """Intermediate model for Order-Product relationship with quantity"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)  # Price at order time
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['order', 'product']
    
    @property
    def total_price(self):
        return (self.price_at_time * self.quantity) - self.discount
    
    def save(self, *args, **kwargs):
        if not self.price_at_time:
            self.price_at_time = self.product.price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.order_number}"

class InventoryTransaction(models.Model):
    """Track inventory changes"""
    
    class TransactionType(models.TextChoices):
        RECEIVED = 'received', 'Received'
        SOLD = 'sold', 'Sold'
        RETURNED = 'returned', 'Returned'
        ADJUSTMENT = 'adjustment', 'Adjustment'
        DAMAGED = 'damaged', 'Damaged'
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_transactions')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_transactions')
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    quantity = models.IntegerField()  # Positive for received, negative for sold/damaged
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_type}: {self.product.name} - {self.quantity} units"

class CustomerNote(models.Model):
    """Notes about customers"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notes')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    note = models.TextField()
    is_private = models.BooleanField(default=True)  # Private notes for staff only
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note for {self.customer.name} - {self.created_at.date()}"