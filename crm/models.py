from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError
import re

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        if self.phone:
            # Validate phone number format
            phone_pattern = r'^(\+\d{1,3}\d{6,14}|\d{3}-\d{3}-\d{4})$'
            if not re.match(phone_pattern, self.phone):
                raise ValidationError({'phone': 'Invalid phone number format'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.email})"

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, 
                                validators=[MinValueValidator(0.01)])
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - ${self.price}"

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_total(self):
        return sum(product.price for product in self.products.all())
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.pk:  # Only calculate after the order has been saved (for ManyToMany)
            self.total_amount = self.calculate_total()
            super().save(update_fields=['total_amount'])
    
    def __str__(self):
        return f"Order #{self.id} - {self.customer.name} - ${self.total_amount}"