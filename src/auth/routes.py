# for authentication the app uses rest apis
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from src.validators.user_validators import AuthRegisterUserType, AuthLoginUserType
from src.db.database import SessionLocal
from sqlalchemy import select
from src.models.users_model import UserModel
from lib.hash_pass import hash_password, verify_password
from src.utils.tokens import create_refresh_token, create_access_token
from src.utils.auth_validator import auth_validator
from fastapi import Request
from src.models.refresh_token_model import RefreshTokenModel
from lib.redis import redisConnection

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


# login user api route
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
                    detail={"message": "Something went wrong.", "data": {}},
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
    except Exception:
        raise HTTPException(
            status_code=500, detail={"message": "Something went wrong.", "data": {}}
        )


# logout user api route
@auth_routes.post("/logout", status_code=200)
def logout_user(request: Request):
    # validate the cookie and hold the user id
    auth_validation = auth_validator(request)

    if not auth_validation:
        raise HTTPException(
            status_code=401, detail={"message": "User unauthenticated.", "data": {}}
        )

    user_id = auth_validation["user_id"]

    try:
        # delete all the sessions of the user
        with SessionLocal.begin() as session:
            (
                session.query(RefreshTokenModel)
                .filter(user_id == user_id)
                .delete(synchronize_session=False)
            )

        token_hex = str(auth_validation["access_cookie"])

        # delete the access token saved in redis
        redisConnection.delete(f"access_token:{token_hex}")

        # clear the cookies from the client
        response = JSONResponse(
            content={"message": "User logged out."}, status_code=200
        )

        response.delete_cookie(
            key="refresh_token",
            secure=True,
            httponly=True,
            samesite="strict",
        )

        response.delete_cookie(
            key="access_token",
            secure=True,
            httponly=True,
            samesite="strict",
        )

        return response
    except Exception:
        raise HTTPException(
            status_code=500, detail={"message": "Something went wrong.", "data": {}}
        )


# recieve the access token once again
@auth_routes.post("/refresh", status_code=200)
def refresh_user_access_token(request: Request):
    # check if the client already has a access token
    check_existing_access_cookie = request.cookies.get("access_token")

    if check_existing_access_cookie:
        raise HTTPException(
            status_code=403, detail={"message": "Bad request.", "data": {}}
        )

    # validate the cookie and hold the user id
    refresh_cookie = request.cookies.get("refresh_token")

    if not refresh_cookie:
        raise HTTPException(
            status_code=401, detail={"message": "User unauthenticated.", "data": {}}
        )

    try:
        # create session and look for the session with cookie value
        with SessionLocal.begin() as session:
            # if no refresh session, return unauthenticated error response
            get_session_stmt = select(RefreshTokenModel).where(
                RefreshTokenModel.token == refresh_cookie
            )

            check_user_session_exists = (
                session.execute(get_session_stmt).scalars().first()
            )

            if not check_user_session_exists:
                raise HTTPException(
                    status_code=401,
                    detail={"message": "User unauthenticated.", "data": {}},
                )

            # if refresh session is found generate new access token and return to client
            access_token = create_access_token(
                check_user_session_exists.user_id, session
            )

            if not access_token:
                raise HTTPException(
                    status_code=500,
                    detail={"message": "Something went wrong.", "data": {}},
                )

            response = JSONResponse(
                content={"message": "Access refresh successfull.", "data": {}},
                status_code=200,
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
    except Exception:
        raise HTTPException(
            status_code=500, detail={"message": "Something went wrong.", "data": {}}
        )


# delete user reest api
@auth_routes.post("/delete", status_code=200)
def delete_user(request: Request):
    try:
        # validate the user authentication
        auth_validation = auth_validator(request)

        if not auth_validation:
            raise HTTPException(
                status_code=401, detail={"message": "User unauthenticated.", "data": {}}
            )

        # access the returned data
        user_id = auth_validation["user_id"]
        token_hex = auth_validation["access_cookie"]

        # connect to the database
        with SessionLocal.begin() as session:
            # delete the user
            find_user = session.scalars(
                select(UserModel).where(UserModel.id == user_id)
            ).one()

            # session document will be auto deleted
            session.delete(find_user)

        # delete the access token from server
        redisConnection.delete(f"access_token:{token_hex}")

        # construct the json response and delete the cookies
        response = JSONResponse(
            content={
                "message": "User deleted successfully.",
                "data": {"id": str(user_id)},
            },
            status_code=200,
        )

        response.delete_cookie(
            key="refresh_token",
            secure=True,
            httponly=True,
            samesite="strict",
        )

        response.delete_cookie(
            key="access_token",
            secure=True,
            httponly=True,
            samesite="strict",
        )

        return response
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(
            status_code=500, detail={"message": "Something went wrong.", "data": {}}
        )
