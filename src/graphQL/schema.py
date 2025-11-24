from graphene import ObjectType, String, Schema
from src.graphQL.users.mutations import UserMutations


class Query(ObjectType):
    hello = String(first_name=String(default_value="world"))

    def resolve_hello(self, info, first_name):
        return f"Hello {first_name}!"


class Mutation(UserMutations, ObjectType):
    pass


schema = Schema(query=Query, mutation=Mutation)
