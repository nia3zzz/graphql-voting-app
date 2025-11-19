import secrets
from src.models.refresh_token_model import RefreshTokenModel
from lib.redis import redisConnection
from datetime import datetime
from uuid import UUID
from sqlalchemy import select


# create refresh token and store it in db
def create_refresh_token(user_id, session):
    # receive the user id and session from the parent mutation
    try:
        # create a random token and save it in db
        token_hex = secrets.token_hex(16)

        refresh_token = RefreshTokenModel(user_id=user_id, token=token_hex)
        session.add(refresh_token)
        session.flush()

        return token_hex
    except Exception as e:
        raise RuntimeError(f"Error creating refresh token: {e}")


# create access token and store it in redis
def create_access_token(user_id, session):
    # receive the user id and the session from the parent mutation
    try:
        # check if the user has a refresh token

        check_refresh_token_stmt = select(RefreshTokenModel).where(
            RefreshTokenModel.user_id == user_id
        )
        check_refresh_token = (
            session.execute(check_refresh_token_stmt).scalars().first()
        )

        if not check_refresh_token:
            return None

        # create the access token
        token_hex = secrets.token_hex(16)

        redisConnection.set(
            f"access_token:{token_hex}",
            f"user_id:{user_id}",
        )

        redisConnection.expire(f"access_token:{token_hex}", 3600)

        # logic to update the last used time of the refresh token
        check_refresh_token.last_used_at = datetime.now()

        return token_hex
    except Exception as e:
        raise RuntimeError(f"Error creating access token: {e}")


# verify access token from redis
async def verify_access_token(token):
    try:
        user_id = await redisConnection.get(f"access_token:{token}")
        if user_id:
            return UUID(user_id.split(":")[1])
        return None
    except Exception as e:
        raise RuntimeError(f"Error verifying access token: {e}")
