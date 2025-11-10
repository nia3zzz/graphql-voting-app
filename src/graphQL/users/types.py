from graphene_sqlalchemy import SQLAlchemyObjectType
from src.models.users_model import UserModel


class UserType(SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        exclude_fields = ("password", "created_vote_topics", "voted_vote_topics")
