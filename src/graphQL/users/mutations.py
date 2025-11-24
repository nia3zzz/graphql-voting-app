import graphene
from src.validators.user_validators import UpdateUserArgument
from pydantic import ValidationError
from src.utils.auth_validator import auth_validator
from src.db.database import SessionLocal
from sqlalchemy import select
from src.models.users_model import UserModel
from src.graphQL.users.types import UserType


# mutation for updating the user
class UpdateUserMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        email = graphene.String()

    message = graphene.String()
    data = graphene.Field(UserType)

    def __init__(self, message, data):
        self.message = message
        self.data = data

    def mutate(self, info, name, email):
        try:
            # validate user authentication
            auth_validation = auth_validator(info.context["request"])

            if not auth_validation:
                return UpdateUserMutation(message="User unauthenticated.", data=None)

            user_id = auth_validation["user_id"]

            # validation of arguments
            validate = UpdateUserArgument(name=name, email=email)

            # connect to database
            with SessionLocal.begin() as session:
                # select the user
                find_user = session.scalars(
                    select(UserModel).where(UserModel.id == user_id)
                ).one()

                # check if the existing user data is same as the provided data
                if (
                    find_user.name == validate.name
                    and find_user.email == validate.email
                ):
                    return UpdateUserMutation(
                        message="No updating data found.", data=None
                    )

                # update the name and email
                find_user.name = validate.name
                find_user.email = validate.email

                # fill the queried variable with new data and hold the user variable outside session
                session.flush()
                session.expunge(find_user)

                return UpdateUserMutation(
                    message="User updated successfully.", data=find_user
                )
        except ValidationError as e:
            return UpdateUserMutation(message=e.errors()[0]["msg"], data=None)
        except Exception:
            return UpdateUserMutation(message="Something went wrong.", data=None)


# user mutation class to combine all the muration under it
class UserMutations(graphene.ObjectType):
    update_user = UpdateUserMutation.Field()
