#!/bin/bash

# Set the Django environment
cd /alx-backend-graphql_crm/
export DJANGO_SETTINGS_MODULE=crm.settings

# Run the Django shell command to delete inactive customers
DELETED_COUNT=$(python manage.py shell << EOF
from orders.models import Order
from django.utils import timezone
from datetime import timedelta

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders since one year ago
from django.contrib.auth.models import User
inactive_customers = User.objects.filter(order__isnull=True) | User.objects.exclude(order__date__gte=one_year_ago)
count = inactive_customers.count()
inactive_customers.delete()
print(count)
EOF
)

# Log the result with timestamp
echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted $DELETED_COUNT inactive customers" >> /tmp/customer_cleanup_log.txt