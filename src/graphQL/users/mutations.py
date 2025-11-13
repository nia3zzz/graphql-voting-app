import graphene
from validators.user_validators import CreateUserMutationInput
from pydantic import ValidationError
from db.database import SessionLocal
from models.users_model import UserModel
from sqlalchemy import select
from lib.hash_pass import hash_password


class CreateUser(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        email = graphene.String()
        password = graphene.String()

    message = graphene.String()

    def __init__(self, message):
        self.message = message

    def mutate(self, info, name, email, password):
        try:
            validate = CreateUserMutationInput(
                name=name, email=email, password=password
            )
        except ValidationError as e:
            return CreateUser(message=e.errors()[0]["msg"])

        try:
            with SessionLocal.begin() as db_session:
                check_users_exists = select(UserModel).where(
                    UserModel.email == validate.email
                )

                result = db_session.execute(check_users_exists).scalars().first()

                if result is not None:
                    return CreateUser(message="User already exists with this email.")

                hashed_password = hash_password(validate.password)

                new_user = UserModel(
                    name=validate.name, email=validate.email, password=hashed_password
                )
                db_session.add(new_user)
        except Exception as e:
            return CreateUser(message="Something went wrong.")

        return CreateUser(message="User created successfully.")


class UserMutations(graphene.ObjectType):
    create_user = CreateUser.Field()
