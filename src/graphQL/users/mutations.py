import graphene
from src.validators.user_validators import (
    CreateUserMutationInput,
    LoginUserMutationInput,
)
from pydantic import ValidationError
from src.db.database import SessionLocal
from src.models.users_model import UserModel
from sqlalchemy import select
from lib.hash_pass import hash_password, verify_password
from src.utils.tokens import create_refresh_token


# create user mutation
class CreateUser(graphene.Mutation):
    # expected data recieved from client
    class Arguments:
        name = graphene.String()
        email = graphene.String()
        password = graphene.String()

    # response data sent to client
    message = graphene.String()

    # response data constructor
    def __init__(self, message):
        self.message = message

    # main mutation logic
    def mutate(self, info, name, email, password):
        # data validation
        try:
            validate = CreateUserMutationInput(
                name=name, email=email, password=password
            )
        except ValidationError as e:
            return CreateUser(message=e.errors()[0]["msg"])

        # main business logic
        try:
            with SessionLocal.begin() as session:
                check_users_exists = select(UserModel).where(
                    UserModel.email == validate.email
                )

                # check user exists
                result = session.execute(check_users_exists).scalars().first()

                if result is not None:
                    return CreateUser(message="User already exists with this email.")

                # hash password and create user
                hashed_password = hash_password(validate.password)

                new_user = UserModel(
                    name=validate.name, email=validate.email, password=hashed_password
                )
                session.add(new_user)
        except Exception as e:
            return CreateUser(message="Something went wrong.")

        # return success message
        return CreateUser(message="User created successfully.")


# login user mutation
class LoginUser(graphene.Mutation):
    # expected data received from client
    class Arguments:
        email = graphene.String()
        password = graphene.String()

    # response data sent to client
    message = graphene.String()

    # response data constructor
    def __init__(self, message):
        self.message = message

    # main mutation logic
    def mutate(self, info, email, password):
        # data validation
        try:
            validate = LoginUserMutationInput(email=email, password=password)
        except ValidationError as e:
            return LoginUser(message=e.errors()[0]["msg"])

        # main business logic
        try:
            with SessionLocal.begin() as session:
                get_user = select(UserModel).where(UserModel.email == validate.email)

                # fetch user
                user = session.execute(get_user).scalars().first()

                if user is None:
                    return LoginUser(message="Invalid email or password.")

                # check password
                check_password = verify_password(validate.password, user.password)

                if not check_password:
                    return LoginUser(message="Invalid email or password.")

                # create a refresh token
                refresh_token = create_refresh_token(user.id, session)

        except:
            return LoginUser(message="Something went wrong.")

        return LoginUser(message="Login successful.")


class UserMutations(graphene.ObjectType):
    create_user = CreateUser.Field()
    login_user = LoginUser.Field()
