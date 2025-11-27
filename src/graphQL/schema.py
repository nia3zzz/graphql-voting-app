from graphene import ObjectType, String, Schema
from src.graphQL.users.mutations import UserMutations
from src.graphQL.users.queries import UserQuerys

# construct the parent classes by providing child classes as parameters in query, mutation and subscription

class Query(UserQuerys, ObjectType):
    hello = String(first_name=String(default_value="world"))

    def resolve_hello(self, info, first_name):
        return f"Hello {first_name}!"


class Mutation(UserMutations, ObjectType):
    pass


schema = Schema(query=Query, mutation=Mutation)
