import graphene
from src.utils.auth_validator import auth_validator
from src.db.database import SessionLocal
from sqlalchemy import select, desc
from src.graphQL.vote_topics.types import GetVoteTopicsType
from src.validators.vote_topic_validators import GetVoteTopicsInputTypeValidator
from pydantic import ValidationError
from src.models.vote_topics_model import VoteTopicModel


# response wrapper
class GetVoteTopicsQueryResponse(graphene.ObjectType):
    status = graphene.Boolean()
    message = graphene.String()
    data = graphene.Field(graphene.List(GetVoteTopicsType))

    def __init__(self, status: bool, message: str, data=None):
        self.status = status
        self.message = message
        self.data = data


# vote topic queries parent class
class VoteTopicQuerys(graphene.ObjectType):
    # define the query
    get_vote_topics = graphene.Field(
        GetVoteTopicsQueryResponse,
        limit=graphene.Int(required=False),
        skip=graphene.Int(required=False),
    )

    # resolve the defined query
    def resolve_get_vote_topics(self, info, limit=10, skip=0):
        # validate the user
        auth_validation = auth_validator(info.context["request"])

        if not auth_validation:
            return GetVoteTopicsQueryResponse(
                status=False, message="User not authenticated.", data=None
            )

        try:
            # validation of user query input
            validate = GetVoteTopicsInputTypeValidator(limit=limit, skip=skip)

            # start up the database session
            with SessionLocal.begin() as session:
                # select the vote topics
                vote_topics = session.scalars(
                    select(VoteTopicModel)
                    .offset(validate.skip)
                    .limit(validate.limit)
                    .order_by(desc(VoteTopicModel.created_at))
                ).all()

                for vote_topic in vote_topics:
                    session.expunge(vote_topic)

            return GetVoteTopicsQueryResponse(
                status=True, message="Vote topics data fetched.", data=vote_topics
            )

        except ValidationError as e:
            return GetVoteTopicsQueryResponse(
                status=False, message=e.errors()[0]["msg"], data=None
            )
        except Exception:
            return GetVoteTopicsQueryResponse(
                status=False, message="Something went wrong.", data=None
            )
