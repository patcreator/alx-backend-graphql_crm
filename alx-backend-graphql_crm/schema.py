import graphene
from crm.schema import Query as CRMQuery, Mutation as CRMMutation

class Query(CRMQuery, graphene.ObjectType):
    """
    Root Query class that combines all query definitions from different apps.
    Currently includes CRM queries, but can be extended with other app queries.
    """
    # You can add project-specific queries here if needed
    hello = graphene.String()
    
    def resolve_hello(self, info):
        """
        Simple hello world query to test the GraphQL endpoint.
        """
        return "Hello, GraphQL!"

class Mutation(CRMMutation, graphene.ObjectType):
    """
    Root Mutation class that combines all mutation definitions from different apps.
    Currently includes CRM mutations.
    """
    pass

# Create the GraphQL schema
schema = graphene.Schema(query=Query, mutation=Mutation)

# Optional: Add subscription support if needed
# class Subscription(graphene.ObjectType):
#     pass

# schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)
