import graphene
from src.utils.auth_validator import auth_validator
from src.db.database import SessionLocal
from sqlalchemy import select
from src.validators.vote_options_validators import GetVoteOptionsInputTypeValidator
from pydantic import ValidationError
from src.graphQL.votes.types import GetVoteOptionsType
from src.models.votes_model import VoteModel
from src.models.vote_topics_model import VoteTopicModel


# response wrapper
class GetVoteOptionsQueryResponse(graphene.ObjectType):
    status = graphene.Boolean()
    message = graphene.String()
    data = graphene.Field(graphene.List(GetVoteOptionsType))

    def __init__(self, status: bool, message: str, data=None):
        self.status = status
        self.message = message
        self.data = data


# vote option queries parent class
class VoteOptionQuerys(graphene.ObjectType):
    # define the query
    get_vote_options = graphene.Field(
        GetVoteOptionsQueryResponse, vote_topic_id=graphene.String(required=True)
    )

    # resolve the defined query
    def resolve_get_vote_options(self, info, vote_topic_id):
        # validate the user
        auth_validation = auth_validator(info.context["request"])

        if not auth_validation:
            return GetVoteOptionsQueryResponse(
                status=False, message="User unauthenticated.", data=None
            )

        try:
            # validation of user query input
            validate = GetVoteOptionsInputTypeValidator(vote_topic_id=vote_topic_id)

            # start up the database session
            with SessionLocal.begin() as session:
                # check if the vote topic exists
                vote_topic = session.scalars(
                    select(VoteTopicModel).where(
                        VoteTopicModel.id == validate.vote_topic_id
                    )
                ).first()

                if not vote_topic:
                    return GetVoteOptionsQueryResponse(
                        status=False, message="Vote topic not found.", data=None
                    )

                # select the vote options
                vote_options = session.scalars(
                    select(VoteModel).where(
                        VoteModel.vote_topic_id == validate.vote_topic_id
                    )
                ).all()

                # hold the variables out of session
                for vote_option in vote_options:
                    session.expunge(vote_option)

            return GetVoteOptionsQueryResponse(
                status=True, message="Vote options data fetched.", data=vote_options
            )

        except ValidationError as e:
            return GetVoteOptionsQueryResponse(
                status=False, message=e.errors()[0]["msg"], data=None
            )
        except Exception:
            return GetVoteOptionsQueryResponse(
                status=False, message="Something went wrong.", data=None
            )
