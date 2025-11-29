import graphene
from src.validators.vote_topic_validators import (
    CreateVoteTopicArgumentTypeValidator,
    DeleteVoteTopicArgumentTypeValidator,
)
from pydantic import ValidationError
from src.utils.auth_validator import auth_validator
from src.db.database import SessionLocal
from src.models.vote_topics_model import VoteTopicModel
from src.models.votes_model import VoteModel
from src.graphQL.vote_topics.types import VoteTopicType
from sqlalchemy import select


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


class DeleteVoteTopicMutation(graphene.Mutation):
    class Arguments:
        vote_topc_id = graphene.String()

    status = graphene.Boolean()
    message = graphene.String()
    data = graphene.Field(VoteTopicType)

    def __init__(self, status, message, data):
        self.status = status
        self.message = message
        self.data = data

    def mutate(self, info, vote_topc_id):
        # validate the user auth
        auth_validation = auth_validator(info.context["request"])

        if not auth_validation:
            return DeleteVoteTopicMutation(
                status=False, message="User unauthenticated.", data=None
            )

        user_id = auth_validation["user_id"]

        try:
            # validate the input arguments
            validate = DeleteVoteTopicArgumentTypeValidator(vote_topic_id=vote_topc_id)

            # open data base session
            with SessionLocal.begin() as session:

                # check if a vote topic exists with the provided vote topic id and user making request is the author

                find_vote_topic = session.scalars(
                    select(VoteTopicModel).where(
                        VoteTopicModel.id == validate.vote_topic_id
                    )
                ).first()
                
                if not find_vote_topic or find_vote_topic.created_by != user_id:
                    return DeleteVoteTopicMutation(
                        status=False,
                        message="Vote topic could not be deleted.",
                        data=None,
                    )

                # remove the vote topic from the session to send back to client
                out_session_vote_topic = find_vote_topic
                session.expunge(out_session_vote_topic)

                # delete the vote topic
                session.delete(find_vote_topic)

                return DeleteVoteTopicMutation(
                    status=True,
                    message="Vote topic deleted successfully.",
                    data=out_session_vote_topic,
                )
        except ValidationError as e:
            return DeleteVoteTopicMutation(
                status=False, message=e.errors()[0]["msg"], data=None
            )
        except Exception:
            return DeleteVoteTopicMutation(
                status=False, message="Something went wrong.", data=None
            )


# vote topic mutation class to combine all the murations under it
class VoteTopicMutations(graphene.ObjectType):
    create_vote_topic = CreateVoteTopicMutation.Field()
    delete_vote_topic = DeleteVoteTopicMutation.Field()
