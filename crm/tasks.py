import os
import sys
from datetime import datetime
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# GraphQL query for CRM report
CRM_REPORT_QUERY = gql("""
query {
  customers: users {
    id
  }
  orders: orders {
    id
    totalAmount
  }
}
""")

@shared_task
def generate_crm_report():
    """
    Generate weekly CRM report with total customers, orders, and revenue
    """
    try:
        # Setup GraphQL client
        transport = RequestsHTTPTransport(
            url='http://localhost:8000/graphql',
            verify=False,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # Execute query
        result = client.execute(CRM_REPORT_QUERY)
        
        # Calculate totals
        total_customers = len(result.get('customers', []))
        total_orders = len(result.get('orders', []))
        
        # Calculate total revenue
        total_revenue = sum(
            order.get('totalAmount', 0) 
            for order in result.get('orders', [])
        )
        
        # Format timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Log the report
        log_message = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, ${total_revenue:.2f} revenue\n"
        
        # Ensure the /tmp directory exists in Windows/WSL
        log_dir = '/tmp'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        with open('/tmp/crm_report_log.txt', 'a') as log_file:
            log_file.write(log_message)
        
        return {
            'status': 'success',
            'timestamp': timestamp,
            'customers': total_customers,
            'orders': total_orders,
            'revenue': total_revenue
        }
        
    except Exception as e:
        error_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR generating report: {str(e)}\n"
        
        with open('/tmp/crm_report_log.txt', 'a') as log_file:
            log_file.write(error_message)
        
        return {
            'status': 'error',
            'error': str(e)
        }