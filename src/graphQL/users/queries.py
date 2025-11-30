import graphene
from src.graphQL.users.types import UserType
from src.utils.auth_validator import auth_validator
from src.db.database import SessionLocal
from sqlalchemy import select
from src.models.users_model import UserModel


# response wrapper
class GetUserProfileQueryResponse(graphene.ObjectType):
    status = graphene.Boolean()
    message = graphene.String()
    data = graphene.Field(UserType)

    def __init__(self, status: bool, message: str, data=None):
        self.status = status
        self.message = message
        self.data = data


# user queries parent class
class UserQuerys(graphene.ObjectType):
    # define the queries with their response type
    get_user_profile = graphene.Field(GetUserProfileQueryResponse)

    # resolvers for the defined queries
    def resolve_get_user_profile(self, info):
        # validate the user
        auth_validation = auth_validator(info.context["request"])

        if not auth_validation:
            return GetUserProfileQueryResponse(
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

                return GetUserProfileQueryResponse(
                    status=True, message="User data recieved.", data=find_user
                )
        except Exception:
            return GetUserProfileQueryResponse(
                status=False, message="Something went wrong.", data=None
            )
