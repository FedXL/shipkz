import jwt
import time

def generate_jwt_token(user_id, username):
    # Set the secret key for signing the token (should be long and complex)
    secret_key = 'SuperPuperCriptoSecret!#!@)(*_)%$ADawdawW:'
    current_time = int(time.time())
    expiration_time = current_time + 20
    payload = {
        "user_id": user_id,
        "username": username,
        "current_time": current_time,
        "exp": expiration_time
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token