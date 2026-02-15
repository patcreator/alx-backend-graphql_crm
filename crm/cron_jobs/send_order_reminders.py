#!/usr/bin/env python3

import os
import sys
import json
from datetime import datetime, timedelta
import requests
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Setup Django environment
sys.path.append('/alx-backend-graphql_crm/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')

# GraphQL query for recent orders
RECENT_ORDERS_QUERY = gql("""
query GetRecentOrders($days: Int!) {
  orders(orderDate_gte: $days) {
    id
    customer {
      email
    }
    orderDate
    status
  }
}
""")

def send_order_reminders():
    """Query recent orders and log reminders"""
    try:
        # Setup GraphQL client
        transport = RequestsHTTPTransport(
            url='http://localhost:8000/graphql',
            verify=False,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # Query orders from last 7 days
        variables = {'days': 7}
        result = client.execute(RECENT_ORDERS_QUERY, variable_values=variables)
        
        # Log each pending order
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            for order in result.get('orders', []):
                log_file.write(f"{timestamp} - Order ID: {order['id']}, Customer Email: {order['customer']['email']}\n")
            
            print("Order reminders processed!")
            
    except Exception as e:
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_file.write(f"{timestamp} - ERROR: {str(e)}\n")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    send_order_reminders()