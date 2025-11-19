from fastapi import Request
from src.utils.tokens import verify_access_token


# a auth cookie validator helper function used within controller logic in rest apis and graphql logics,
def auth_validator(request: Request):
    access_cookie = request.cookies.get("access_token")

    if not access_cookie:
        return None

    user_id = verify_access_token(access_cookie)

    if not user_id:
        return None

    return {"user_id": user_id, "access_cookie": access_cookie}
