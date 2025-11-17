from graphene_sqlalchemy import SQLAlchemyObjectType
from src.models.vote_topics_model import VoteTopicModel
from src.graphQL.users.types import UserType
from graphene import Field


class VoteTopicType(SQLAlchemyObjectType):
    class Meta:
        model = VoteTopicModel
        exclude_fields = ("creator", "voters", "voting_options")

    creator = Field(UserType)
