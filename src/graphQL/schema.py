from graphene import ObjectType, String, Schema
from src.graphQL.users.mutations import UserMutations
from src.graphQL.users.queries import UserQuerys
from src.graphQL.vote_topics.mutations import VoteTopicMutations
from src.graphQL.vote_topics.queries import VoteTopicQuerys
from src.graphQL.votes.mutations import VoteTopicOptionMutations

# construct the parent classes by providing child classes as parameters in query, mutation and subscription


class Query(UserQuerys, VoteTopicQuerys, ObjectType):
    hello = String(first_name=String(default_value="world"))

    def resolve_hello(self, info, first_name):
        return f"Hello {first_name}!"


class Mutation(UserMutations, VoteTopicMutations, VoteTopicOptionMutations, ObjectType):
    pass


schema = Schema(query=Query, mutation=Mutation)
