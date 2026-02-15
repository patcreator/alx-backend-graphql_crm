from django.core.management.base import BaseCommand
from crm.models import Customer, Product, Order
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seed the database with sample data'
    
    def handle(self, *args, **kwargs):
        # Clear existing data
        Order.objects.all().delete()
        Product.objects.all().delete()
        Customer.objects.all().delete()
        
        # Create customers
        customers = [
            Customer(name="Alice Johnson", email="alice@example.com", phone="+1234567890"),
            Customer(name="Bob Smith", email="bob@example.com", phone="987-654-3210"),
            Customer(name="Carol Davis", email="carol@example.com", phone="555-123-4567"),
            Customer(name="David Brown", email="david@example.com", phone="+44123456789"),
            Customer(name="Eva Wilson", email="eva@example.com", phone=""),
        ]
        
        for customer in customers:
            customer.save()
            self.stdout.write(f"Created customer: {customer.name}")
        
        # Create products
        products = [
            Product(name="Laptop", price=Decimal("999.99"), stock=10),
            Product(name="Mouse", price=Decimal("29.99"), stock=50),
            Product(name="Keyboard", price=Decimal("79.99"), stock=30),
            Product(name="Monitor", price=Decimal("299.99"), stock=15),
            Product(name="Headphones", price=Decimal("149.99"), stock=25),
        ]
        
        for product in products:
            product.save()
            self.stdout.write(f"Created product: {product.name}")
        
        # Create orders
        for i in range(5):
            customer = random.choice(customers)
            num_products = random.randint(1, 3)
            selected_products = random.sample(products, num_products)
            
            order = Order(customer=customer)
            order.save()
            order.products.set(selected_products)
            order.total_amount = sum(p.price for p in selected_products)
            order.save()
            
            self.stdout.write(f"Created order #{order.id} for {customer.name}")
        
        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))