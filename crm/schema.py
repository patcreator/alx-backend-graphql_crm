import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField  # Add this import
from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)

# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

# Mutation: CreateCustomer
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)
    
    customer = graphene.Field(CustomerType)
    message = graphene.String()
    
    def mutate(self, info, input):
        try:
            # Check for duplicate email
            if Customer.objects.filter(email=input.email).exists():
                raise ValidationError(f"Email '{input.email}' already exists")
            
            customer = Customer(
                name=input.name,
                email=input.email,
                phone=input.phone
            )
            customer.save()
            
            return CreateCustomer(
                customer=customer,
                message="Customer created successfully"
            )
        except ValidationError as e:
            raise Exception(str(e))
        except Exception as e:
            raise Exception(f"Error creating customer: {str(e)}")

# Mutation: BulkCreateCustomers
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)
    
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, input):
        created_customers = []
        errors = []
        
        with transaction.atomic():
            for customer_data in input:
                try:
                    # Check for duplicate email
                    if Customer.objects.filter(email=customer_data.email).exists():
                        errors.append(f"Email '{customer_data.email}' already exists")
                        continue
                    
                    customer = Customer(
                        name=customer_data.name,
                        email=customer_data.email,
                        phone=customer_data.phone
                    )
                    customer.save()
                    created_customers.append(customer)
                except Exception as e:
                    errors.append(f"Error creating {customer_data.email}: {str(e)}")
        
        return BulkCreateCustomers(customers=created_customers, errors=errors)

# Mutation: CreateProduct
class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)
    
    product = graphene.Field(ProductType)
    
    def mutate(self, info, input):
        try:
            if input.price <= 0:
                raise ValidationError("Price must be positive")
            
            if input.stock is not None and input.stock < 0:
                raise ValidationError("Stock cannot be negative")
            
            product = Product(
                name=input.name,
                price=input.price,
                stock=input.stock if input.stock is not None else 0
            )
            product.save()
            
            return CreateProduct(product=product)
        except ValidationError as e:
            raise Exception(str(e))
        except Exception as e:
            raise Exception(f"Error creating product: {str(e)}")

# Mutation: CreateOrder
class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)
    
    order = graphene.Field(OrderType)
    
    def mutate(self, info, input):
        try:
            # Validate customer exists
            try:
                customer = Customer.objects.get(id=input.customer_id)
            except Customer.DoesNotExist:
                raise ValidationError(f"Customer with ID {input.customer_id} does not exist")
            
            # Validate products exist
            products = []
            for product_id in input.product_ids:
                try:
                    product = Product.objects.get(id=product_id)
                    products.append(product)
                except Product.DoesNotExist:
                    raise ValidationError(f"Product with ID {product_id} does not exist")
            
            if not products:
                raise ValidationError("At least one product must be selected")
            
            # Create order
            order = Order(customer=customer)
            order.save()  # Save first to get an ID
            
            # Add products
            order.products.set(products)
            
            # Calculate total
            order.total_amount = sum(product.price for product in products)
            order.save()
            
            return CreateOrder(order=order)
        except ValidationError as e:
            raise Exception(str(e))
        except Exception as e:
            raise Exception(f"Error creating order: {str(e)}")

# Filter Input Types
class CustomerFilterInput(graphene.InputObjectType):
    name_icontains = graphene.String()
    email_icontains = graphene.String()
    created_at_gte = graphene.DateTime()
    created_at_lte = graphene.DateTime()
    phone_pattern = graphene.String()

class ProductFilterInput(graphene.InputObjectType):
    name_icontains = graphene.String()
    price_gte = graphene.Decimal()
    price_lte = graphene.Decimal()
    stock_gte = graphene.Int()
    stock_lte = graphene.Int()
    low_stock = graphene.Boolean()

class OrderFilterInput(graphene.InputObjectType):
    total_amount_gte = graphene.Decimal()
    total_amount_lte = graphene.Decimal()
    order_date_gte = graphene.DateTime()
    order_date_lte = graphene.DateTime()
    customer_name_icontains = graphene.String()
    product_name_icontains = graphene.String()
    product_id = graphene.ID()

# Query class
class Query(graphene.ObjectType):
    # Basic queries
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)
    customer = graphene.Field(CustomerType, id=graphene.ID(required=True))
    product = graphene.Field(ProductType, id=graphene.ID(required=True))
    order = graphene.Field(OrderType, id=graphene.ID(required=True))
    
    # Filtered queries using DjangoFilterConnectionField
    all_customers = DjangoFilterConnectionField(
        CustomerType, 
        filterset_class=CustomerFilter,
        filter=graphene.Argument(CustomerFilterInput)
    )
    all_products = DjangoFilterConnectionField(
        ProductType, 
        filterset_class=ProductFilter,
        filter=graphene.Argument(ProductFilterInput),
        order_by=graphene.String()
    )
    all_orders = DjangoFilterConnectionField(
        OrderType, 
        filterset_class=OrderFilter,
        filter=graphene.Argument(OrderFilterInput)
    )
    
    # Basic resolvers
    def resolve_customers(self, info):
        return Customer.objects.all()
    
    def resolve_products(self, info):
        return Product.objects.all()
    
    def resolve_orders(self, info):
        return Order.objects.all()
    
    def resolve_customer(self, info, id):
        try:
            return Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            return None
    
    def resolve_product(self, info, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            return None
    
    def resolve_order(self, info, id):
        try:
            return Order.objects.get(id=id)
        except Order.DoesNotExist:
            return None
    
    # Filtered resolvers
    def resolve_all_customers(self, info, **kwargs):
        queryset = Customer.objects.all()
        filter_input = kwargs.get('filter')
        
        if filter_input:
            if filter_input.name_icontains:
                queryset = queryset.filter(name__icontains=filter_input.name_icontains)
            if filter_input.email_icontains:
                queryset = queryset.filter(email__icontains=filter_input.email_icontains)
            if filter_input.created_at_gte:
                queryset = queryset.filter(created_at__gte=filter_input.created_at_gte)
            if filter_input.created_at_lte:
                queryset = queryset.filter(created_at__lte=filter_input.created_at_lte)
            if filter_input.phone_pattern:
                queryset = queryset.filter(phone__startswith=filter_input.phone_pattern)
        
        return queryset
    
    def resolve_all_products(self, info, **kwargs):
        queryset = Product.objects.all()
        filter_input = kwargs.get('filter')
        order_by = kwargs.get('order_by')
        
        if filter_input:
            if filter_input.name_icontains:
                queryset = queryset.filter(name__icontains=filter_input.name_icontains)
            if filter_input.price_gte:
                queryset = queryset.filter(price__gte=filter_input.price_gte)
            if filter_input.price_lte:
                queryset = queryset.filter(price__lte=filter_input.price_lte)
            if filter_input.stock_gte:
                queryset = queryset.filter(stock__gte=filter_input.stock_gte)
            if filter_input.stock_lte:
                queryset = queryset.filter(stock__lte=filter_input.stock_lte)
            if filter_input.low_stock:
                queryset = queryset.filter(stock__lt=10)
        
        if order_by:
            queryset = queryset.order_by(order_by)
        
        return queryset
    
    def resolve_all_orders(self, info, **kwargs):
        queryset = Order.objects.all()
        filter_input = kwargs.get('filter')
        
        if filter_input:
            if filter_input.total_amount_gte:
                queryset = queryset.filter(total_amount__gte=filter_input.total_amount_gte)
            if filter_input.total_amount_lte:
                queryset = queryset.filter(total_amount__lte=filter_input.total_amount_lte)
            if filter_input.order_date_gte:
                queryset = queryset.filter(order_date__gte=filter_input.order_date_gte)
            if filter_input.order_date_lte:
                queryset = queryset.filter(order_date__lte=filter_input.order_date_lte)
            if filter_input.customer_name_icontains:
                queryset = queryset.filter(customer__name__icontains=filter_input.customer_name_icontains)
            if filter_input.product_name_icontains:
                queryset = queryset.filter(products__name__icontains=filter_input.product_name_icontains).distinct()
            if filter_input.product_id:
                queryset = queryset.filter(products__id=filter_input.product_id).distinct()
        
        return queryset

# Mutation class
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()