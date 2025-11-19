from graphene import ObjectType, String, Schema


class Query(ObjectType):
    hello = String(first_name=String(default_value="world"))

    def resolve_hello(self, info, first_name):
        return f"Hello {first_name}!"


schema = Schema(query=Query)
