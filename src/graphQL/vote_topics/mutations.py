import graphene
from src.validators.vote_topic_validators import CreateVoteTopicArgumentTypeValidator
from pydantic import ValidationError
from src.utils.auth_validator import auth_validator
from src.db.database import SessionLocal
from src.models.vote_topics_model import VoteTopicModel
from src.models.votes_model import VoteModel
from src.graphQL.vote_topics.types import VoteTopicType


# mutation for creating a vote topic
class CreateVoteTopicMutation(graphene.Mutation):
    class Arguments:
        description = graphene.String()
        options = graphene.List(graphene.NonNull(graphene.String))

    status = graphene.Boolean()
    message = graphene.String()
    data = graphene.Field(VoteTopicType)

    def __init__(self, status, message, data):
        self.status = status
        self.message = message
        self.data = data

    def mutate(self, info, description, options):
        # validate the user
        auth_validation = auth_validator(info.context["request"])

        if not auth_validation:
            return CreateVoteTopicMutation(
                status=False, message="User unauthenticated.", data=None
            )

        user_id = auth_validation["user_id"]

        try:
            # validate the arguments
            validate = CreateVoteTopicArgumentTypeValidator(
                description=description, options=options
            )

            # start database session
            with SessionLocal.begin() as session:
                # create a vote topic
                vote_topic = VoteTopicModel(
                    description=validate.description, created_by=user_id
                )

                session.add(vote_topic)

                # fill the vote topic with data
                session.flush()

                # create voting options from the provided options
                for option in validate.options:
                    vote_option = VoteModel(
                        vote_option=option, vote_topic_id=vote_topic.id
                    )

                    session.add(vote_option)

                # take the vote topic out of session
                session.expunge(vote_topic)

            return CreateVoteTopicMutation(
                status=True, message="Vote topic has been created.", data=vote_topic
            )

        except ValidationError as e:
            return CreateVoteTopicMutation(
                status=False, message=e.errors()[0]["msg"], data=None
            )
        except Exception:
            return CreateVoteTopicMutation(
                status=False, message="Something went wrong.", data=None
            )


# vote topic mutation class to combine all the murations under it
class VoteTopicMutations(graphene.ObjectType):
    create_vote_topic = CreateVoteTopicMutation.Field()
