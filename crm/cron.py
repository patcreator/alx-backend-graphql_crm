import os
import sys
import requests
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# GraphQL query to test endpoint
HELLO_QUERY = gql("""
query {
  hello
}
""")

def log_crm_heartbeat():
    """Log heartbeat message every 5 minutes"""
    try:
        timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
        
        # Test GraphQL endpoint
        transport = RequestsHTTPTransport(
            url='http://localhost:8000/graphql',
            verify=False,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        try:
            result = client.execute(HELLO_QUERY)
            endpoint_status = "responsive" if result.get('hello') else "unresponsive"
        except Exception as e:
            endpoint_status = f"error: {str(e)}"
        
        # Log heartbeat
        with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
            log_file.write(f"{timestamp} CRM is alive - GraphQL endpoint: {endpoint_status}\n")
            
    except Exception as e:
        timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
        with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
            log_file.write(f"{timestamp} CRM is alive - Error checking endpoint: {str(e)}\n")

def update_low_stock():
    """Update low stock products via GraphQL mutation"""
    try:
        # GraphQL mutation
        MUTATION = gql("""
        mutation {
          updateLowStockProducts {
            success
            message
            updatedProducts {
              id
              name
              stock
            }
          }
        }
        """)
        
        # Setup GraphQL client
        transport = RequestsHTTPTransport(
            url='http://localhost:8000/graphql',
            verify=False,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # Execute mutation
        result = client.execute(MUTATION)
        
        # Log results
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
            log_file.write(f"\n{'='*50}\n")
            log_file.write(f"Timestamp: {timestamp}\n")
            
            mutation_result = result.get('updateLowStockProducts', {})
            
            if mutation_result.get('success'):
                log_file.write(f"Status: SUCCESS\n")
                log_file.write(f"Message: {mutation_result.get('message')}\n")
                
                for product in mutation_result.get('updatedProducts', []):
                    log_file.write(f"Updated - Product: {product['name']}, New Stock: {product['stock']}\n")
            else:
                log_file.write(f"Status: FAILED\n")
                log_file.write(f"Error: {mutation_result.get('message')}\n")
                
    except Exception as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
            log_file.write(f"\n{'='*50}\n")
            log_file.write(f"Timestamp: {timestamp}\n")
            log_file.write(f"ERROR: {str(e)}\n")