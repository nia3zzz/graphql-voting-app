import graphene
from src.graphQL.users.types import UserType
from src.utils.auth_validator import auth_validator
from src.db.database import SessionLocal
from sqlalchemy import select
from src.models.users_model import UserModel


# response wrapper
class UserProfileResponse(graphene.ObjectType):
    status = graphene.Boolean()
    message = graphene.String()
    data = graphene.Field(UserType)


# user queries parent class
class UserQuerys(graphene.ObjectType):
    # define the queries with their response type
    user_profile = graphene.Field(UserProfileResponse)

    # resolvers for the defined queries
    def resolve_user_profile(self, info):
        # validate the user
        auth_validation = auth_validator(info.context["request"])

        if not auth_validation:
            return UserProfileResponse(
                status=False, message="User unauthenticated.", data=None
            )

        # hold the user id returned from the validator function
        user_id = auth_validation["user_id"]

        try:
            # start the session and find the user
            with SessionLocal.begin() as session:
                find_user = session.scalars(
                    select(UserModel).where(UserModel.id == user_id)
                ).one()
                
                # hold the user data outside the session to return it
                session.expunge(find_user)
                
                return UserProfileResponse(
                    status=True, message="User data recieved.", data=find_user
                )
        except Exception:
            return UserProfileResponse(
                status=False, message="Something went wrong.", data=None
            )
