import datetime
import jwt
from django.conf import settings
from dotenv import load_dotenv
from jwt import ExpiredSignatureError, ImmatureSignatureError
from app_front.management.unregister_authorization.unregister_web_users import generate_random_name
from legacy.models import WebUsers


load_dotenv()
sharable_secret=settings.SHARABLE_SECRET
def create_token(username: str,
                 ip: str,
                 user_id: str,
                 secret: str = sharable_secret,
                 timedelta: datetime.timedelta = datetime.timedelta(days=14),
                 ):
    """long token"""
    current_time = datetime.datetime.now()
    expiried_time = current_time + timedelta
    token = jwt.encode({'username': username,
                        'user_id': user_id,
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
    """return decoded token dict  if is_comment=False, else return tuple(decoded_token, comment)"""
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


def token_handler(user_ip, token=None) -> str:
    """return jwt token with ip and webusername load"""
    if not token:
        return handle_no_token(user_ip=user_ip)
    else:
        return handle_token(user_ip=user_ip,token=token)


def handle_no_token(user_ip):
    new_username = generate_random_name()
    new_username = 'UNREG_' + new_username
    web_user = WebUsers.objects.create(web_username=new_username)
    new_token = create_token(username=new_username,
                             user_id=web_user.user_id,
                             ip=user_ip)
    return new_token

def handle_no_token_comeback_version(user_ip):
    """return new token for unregistered user"""
    new_username = generate_random_name()
    new_username = 'UNREG_' + new_username
    web_user = WebUsers.objects.create(web_username=new_username)
    new_token = create_token(username=new_username,
                             user_id=web_user.user_id,
                             ip=user_ip)
    return new_token, web_user


def handle_token(user_ip, token):
    decoded_token = check_token(token)
    if decoded_token:
        return token
    else:
        return handle_no_token(user_ip)





