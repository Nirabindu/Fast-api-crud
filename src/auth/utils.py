import logging
import uuid
from datetime import datetime, timedelta

import jwt
from passlib.context import CryptContext

from src.config import Config

password_context = CryptContext(schemes=["bcrypt"])

# In Second
ACCESS_TOKEN_EXPIRY = 3600


def generate_password_hash(password: str) -> str:
    """This Function used create Hash of user-provided password

    Args:
        password (str): user-provided password

    Returns:
        str: return hash password
    """
    hash = password_context.hash(password)
    return hash


def verify_password(password: str, hash_password: str) -> bool:
    """This method used to verify the password with Hash Password

    Args:
        password (str): user-provided password
        hash_password (str): db-store password

    Returns:
        bool: return True if Password Verify else False
    """
    return password_context.verify(password, hash_password)


def create_access_token(
    user_data: dict, expiry: timedelta = None, refresh: bool = False
) -> str:
    """Used to create Token

    Args:
        user_data (dict): _user-data including user-email and uid
        expiry (timedelta, optional): Expiry time of token. Defaults to None.
        refresh (bool, optional): if True creating refresh Token. Defaults to False.

    Returns:
        _type_: _description_
    """
    payload = {}
    payload["user"] = user_data
    payload["exp"] = datetime.now() + (
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)
    )
    # its a id of token nothing else
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh

    token = jwt.encode(
        payload=payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM
    )
    return token


def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    except jwt.PyJWTError as e:

        logging.exception(e)
        return None
