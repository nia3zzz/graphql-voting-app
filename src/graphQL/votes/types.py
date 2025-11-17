from graphene_sqlalchemy import SQLAlchemyObjectType
from src.models.votes_model import VoteModel


class VoteType(SQLAlchemyObjectType):
    class Meta:
        model = VoteModel
        exclude_fields = ("vote_topic",)
