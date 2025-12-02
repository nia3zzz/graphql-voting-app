from graphene_sqlalchemy import SQLAlchemyObjectType
from src.models.votes_model import VoteModel
from src.models.vote_topics_model import VoteTopicModel
from src.db.database import SessionLocal
from sqlalchemy import select


class VoteType(SQLAlchemyObjectType):
    class Meta:
        model = VoteModel
        exclude_fields = ("vote_topic_id",)

    # custom resolver for accessing the vote topic
    def resolve_vote_topic(self, info, **kwargs):
        with SessionLocal.begin() as session:
            vote_topic = session.scalars(
                select(VoteTopicModel).where(VoteTopicModel.id == self.vote_topic_id)
            ).first()
            session.expunge(vote_topic)
        return vote_topic
