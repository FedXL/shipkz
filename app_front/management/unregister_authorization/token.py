import datetime
import os

import jwt
from dotenv import load_dotenv
from jwt import ExpiredSignatureError, ImmatureSignatureError

load_dotenv()
sharable_secret = os.getenv('SHARABLE_SECRET')

def create_token(username: str,
                 ip: str,
                 secret: str = sharable_secret,
                 timedelta: datetime.timedelta = datetime.timedelta(days=14)):
    """long token"""
    current_time = datetime.datetime.now()
    expiried_time = current_time + timedelta
    token = jwt.encode({'username': username,
                        'user_id': 0,
                        'ip': ip,
                        'iat': current_time,
                        'exp': expiried_time},
                       key=secret,
                       algorithm='HS256')
    return token


def create_access_token(username: str, secret=sharable_secret, user_id=0):
    """access token"""
    current_time = datetime.datetime.now()
    expiried_time = current_time + datetime.timedelta(seconds=30)
    token_data = {
        'username': username,
        'user_id': user_id,
        'iat': current_time,
        'exp': expiried_time
    }
    token = jwt.encode(token_data, key=secret, algorithm='HS256')
    return token

def check_token(token: str, secret=sharable_secret, is_comment=False) -> tuple[dict | None, str] | None | dict:
    comment, decoded_token = None, None
    try:
        decoded_token = jwt.decode(token, secret, algorithms=["HS256"], verify=True)
        comment = "Token is valid"
    except ExpiredSignatureError:
        comment = "Invalid Token. Details: Expired"
    except ImmatureSignatureError:
        comment = "Invalid Token. Details: Not yet valid. iat in the future"
    except jwt.DecodeError:
        comment = "Invalid Token. Details: Decoder error. Bad structure in token"
    except Exception as e:
        comment = f"Unexpected error: {e.args}"
    finally:
        if is_comment:
            return decoded_token, comment
        else:
            return decoded_token
