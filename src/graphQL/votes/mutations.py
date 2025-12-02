import graphene
from src.validators.vote_options_validators import (
    AddVoteOptionArgumentTypeValidator,
    CastVoteArgumentTypeValidator,
)
from pydantic import ValidationError
from src.utils.auth_validator import auth_validator
from src.db.database import SessionLocal
from src.models.vote_topics_model import VoteTopicModel
from src.models.votes_model import VoteModel
from sqlalchemy import select
from src.graphQL.votes.types import VoteType
from src.models.association_table import voters_association_table


# mutation for adding a vote option under a vote topic
class AddVoteOptionMutation(graphene.Mutation):
    class Arguments:
        vote_topic_id = graphene.String()
        option = graphene.String()

    status = graphene.Boolean()
    message = graphene.String()
    data = graphene.Field(VoteType)

    def __init__(self, status, message, data):
        self.status = status
        self.message = message
        self.data = data

    def mutate(self, info, vote_topic_id, option):
        # verify the user auth
        auth_validation = auth_validator(info.context["request"])

        if not auth_validation:
            return AddVoteOptionMutation(
                status=False, message="User unauthenticated.", data=None
            )

        try:
            # validate the vote topic id argument
            validate = AddVoteOptionArgumentTypeValidator(
                vote_topic_id=vote_topic_id, option=option
            )

            # open up the database session
            with SessionLocal.begin() as session:
                find_vote_topic = session.scalars(
                    select(VoteTopicModel).where(
                        VoteTopicModel.id == validate.vote_topic_id
                    )
                ).first()

                if not find_vote_topic:
                    return AddVoteOptionMutation(
                        status=False, message="Vote topic not found.", data=None
                    )

                # check if a option with the same value already exists
                find_vote_option = session.scalars(
                    select(VoteModel).where(
                        VoteModel.vote_topic_id == validate.vote_topic_id,
                        VoteModel.vote_option == validate.option,
                    )
                ).first()

                if find_vote_option:
                    return AddVoteOptionMutation(
                        status=False, message="Vote option already exists.", data=None
                    )

                # create the vote option
                vote_option = VoteModel(
                    vote_option=option, vote_topic_id=validate.vote_topic_id
                )

                session.add(vote_option)
                session.flush()

                # get the vote option out of the session and return to client
                session.expunge(vote_option)

                return AddVoteOptionMutation(
                    status=True,
                    message="Vote option added successfully.",
                    data=vote_option,
                )

        except ValidationError as e:
            return AddVoteOptionMutation(
                status=False, message=e.errors()[0]["msg"], data=None
            )
        except Exception:
            return AddVoteOptionMutation(
                status=False, message="Something went wrong.", data=None
            )


# mutation for casting a vote in vote options
class CastVoteMutation(graphene.Mutation):
    class Arguments:
        vote_option_id = graphene.String()

    status = graphene.Boolean()
    message = graphene.String()
    data = graphene.Field(VoteType)

    def __init__(self, status, message, data):
        self.status = status
        self.message = message
        self.data = data

    def mutate(self, info, vote_option_id):
        # verify the user auth
        auth_validation = auth_validator(info.context["request"])

        if not auth_validation:
            return CastVoteMutation(
                status=False, message="User unauthenticated.", data=None
            )

        user_id = auth_validation["user_id"]

        try:
            # validate the vote option id argument
            validate = CastVoteArgumentTypeValidator(vote_option_id=vote_option_id)

            # open up the database session
            with SessionLocal.begin() as session:
                find_vote_option = session.scalars(
                    select(VoteModel).where(VoteModel.id == validate.vote_option_id)
                ).first()

                if not find_vote_option:
                    return CastVoteMutation(
                        status=False, message="Vote option not found.", data=None
                    )

                # check if the user has already voted for this option
                check_user_already_voted = session.scalars(
                    select(voters_association_table).where(
                        voters_association_table.c.user_id == user_id,
                        voters_association_table.c.vote_topic_id
                        == find_vote_option.vote_topic_id,
                    )
                ).first()

                if check_user_already_voted:
                    return CastVoteMutation(
                        status=False, message="User has already voted.", data=None
                    )

                # increment the vote count
                find_vote_option.vote_count += 1

                # add the user to the voters association table
                user_voted = voters_association_table.insert().values(
                    user_id=user_id, vote_topic_id=find_vote_option.vote_topic_id
                )

                # execute and flush vriables
                session.execute(user_voted)

                session.flush()

                # get the updated vote option out of the session and return to client
                session.expunge(find_vote_option)

                return CastVoteMutation(
                    status=True,
                    message="Vote cast successfully.",
                    data=find_vote_option,
                )
        except ValidationError as e:
            return AddVoteOptionMutation(
                status=False, message=e.errors()[0]["msg"], data=None
            )
        except Exception:
            return CastVoteMutation(
                status=False, message="Something went wrong.", data=None
            )


# vote topic option mutation class to combine all the murations under it
class VoteTopicOptionMutations(graphene.ObjectType):
    add_vote_option = AddVoteOptionMutation.Field()
    cast_vote = CastVoteMutation.Field()
