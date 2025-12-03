import graphene
import asyncio
from src.graphQL.votes.types import VoteCountUpdateType
from src.utils.auth_validator import auth_validator
from pydantic import ValidationError
from src.validators.vote_options_validators import VoteCountUpdateInputTypeValidator
from src.db.database import SessionLocal
from sqlalchemy import select
from src.models.vote_topics_model import VoteTopicModel
from src.models.votes_model import VoteModel


# response wrapper for voteCountUpdate subscription
class VoteCountUpdateSubscriptionResponse(graphene.ObjectType):
    status = graphene.Boolean()
    message = graphene.String()
    data = graphene.Field(graphene.List(VoteCountUpdateType))

    def __init__(self, status: bool, message: str, data=None):
        self.status = status
        self.message = message
        self.data = data


class VoteOptionSubscription(graphene.ObjectType):
    vote_count_update = graphene.Field(
        VoteCountUpdateSubscriptionResponse,
        vote_topic_id=graphene.String(required=True),
    )

    async def subscribe_vote_count_update(self, info, vote_topic_id):
        # user auth validation
        auth_validation = auth_validator(info.context["request"])

        if not auth_validation:
            yield VoteCountUpdateSubscriptionResponse(
                status=False, message="User unauthenticated.", data=None
            )

        try:
            # input validation
            validate = VoteCountUpdateInputTypeValidator(vote_topic_id=vote_topic_id)

            # open up database session
            with SessionLocal.begin() as session:
                # check if the vote topic exists
                vote_topic = session.scalars(
                    select(VoteTopicModel).where(
                        VoteTopicModel.id == validate.vote_topic_id
                    )
                ).first()

                if not vote_topic:
                    yield VoteCountUpdateSubscriptionResponse(
                        status=False, message="Vote topic not found.", data=None
                    )

                session.commit()

            # simulate async subscription with a loop
            while True:
                # open up database session
                with SessionLocal.begin() as session:
                    # retrieve all the vote options for the topic
                    vote_options = session.scalars(
                        select(VoteModel).where(
                            VoteModel.vote_topic_id == validate.vote_topic_id
                        )
                    ).all()

                    for vote_option in vote_options:
                        session.expunge(vote_option)

                    session.commit()

                    yield VoteCountUpdateSubscriptionResponse(
                        status=True,
                        message="Vote count received.",
                        data=vote_options,
                    )

                    # wait before sending the next update
                    await asyncio.sleep(10)
        except ValidationError as e:
            yield VoteCountUpdateSubscriptionResponse(
                status=False, message=e.errors()[0]["msg"], data=None
            )
        except Exception:
            yield VoteCountUpdateSubscriptionResponse(
                status=False, message="Something went wrong.", data=None
            )
