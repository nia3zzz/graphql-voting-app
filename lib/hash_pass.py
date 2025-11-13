from bcrypt import hashpw, gensalt, checkpw


def hash_password(plain_password: str):
    salt = gensalt(12)
    hashed_password = hashpw(plain_password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str):
    check_password = checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )
    return check_password
