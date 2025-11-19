# for authentication the app uses rest apis
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from src.validators.user_validators import AuthRegisterUserType, AuthLoginUserType
from src.db.database import SessionLocal
from sqlalchemy import select
from src.models.users_model import UserModel
from lib.hash_pass import hash_password, verify_password
from src.utils.tokens import create_refresh_token, create_access_token

# define auth router with prefix and tags
auth_routes = APIRouter(prefix="/auth", tags=["Auth Routes"])


# create user api route
@auth_routes.post("/register", status_code=201)
def register_user(request_body: AuthRegisterUserType):
    # main business logic
    try:
        with SessionLocal.begin() as session:
            check_user_exists_stmt = select(UserModel).where(
                UserModel.email == request_body.email
            )

            # check user exists
            check_user_exists = (
                session.execute(check_user_exists_stmt).scalars().first()
            )

            if check_user_exists is not None:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": "User already exists with this email.",
                        "data": {},
                    },
                )

            # hash password and create user
            hashed_password = hash_password(request_body.password)

            new_user = UserModel(
                name=request_body.name,
                email=request_body.email,
                password=hashed_password,
            )

            session.add(new_user)
            session.flush()

            return JSONResponse(
                content={
                    "message": "User created successfully.",
                    "data": {"id": str(new_user.id)},
                },
                status_code=201,
            )

    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(
            status_code=500, detail={"message": "Something went wrong.", "data": {}}
        )


@auth_routes.post("/login", status_code=200)
def login_user(request_body: AuthLoginUserType):
    # main business logic
    try:
        with SessionLocal.begin() as session:
            get_user = select(UserModel).where(UserModel.email == request_body.email)

            # fetch user
            check_user_exists = session.execute(get_user).scalars().first()

            if check_user_exists is None:
                raise HTTPException(
                    status_code=401,
                    detail={"message": "Invalid email or password.", "data": {}},
                )

            # check password
            check_password = verify_password(
                request_body.password, check_user_exists.password
            )

            if not check_password:
                raise HTTPException(
                    status_code=401,
                    detail={"message": "Invalid email or password.", "data": {}},
                )

            # create a refresh token
            refresh_token = create_refresh_token(check_user_exists.id, session)

            # create a access token
            access_token = create_access_token(check_user_exists.id, session)

            if not access_token:
                raise HTTPException(
                    status_code=500,
                    detail={"message": "Something went wrong...", "data": {}},
                )

            response = JSONResponse(
                content={"message": "Login successfull.", "data": {}},
                status_code=200,
            )

            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                max_age=3600 * 24 * 15,
                secure=True,
                httponly=True,
                samesite="strict",
            )

            response.set_cookie(
                key="access_token",
                value=access_token,
                max_age=3600,
                secure=True,
                httponly=True,
                samesite="strict",
            )
            return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "Something went wrong.", "data": {}}
        )
