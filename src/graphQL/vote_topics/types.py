from graphene_sqlalchemy import SQLAlchemyObjectType
from src.models.vote_topics_model import VoteTopicModel
from src.graphQL.users.types import UserType
from graphene import Field
from src.db.database import SessionLocal
from src.models.users_model import UserModel
from sqlalchemy import select


class VoteTopicType(SQLAlchemyObjectType):
    class Meta:
        model = VoteTopicModel
        exclude_fields = ("created_by", "voters", "voting_options")

    creator = Field(UserType)

    # custom resolver for accessing the user
    def resolve_creator(self, info, **kwargs):
        with SessionLocal.begin() as session:
            creator = session.scalars(
                select(UserModel).where(UserModel.id == self.created_by)
            ).first()
            session.expunge(creator)
        return creator


class GetVoteTopicsType(SQLAlchemyObjectType):
    class Meta:
        model = VoteTopicModel
        exclude_fields = (
            "created_by",
            "updated_at",
            "creator",
            "voters",
            "voting_options",
        )
