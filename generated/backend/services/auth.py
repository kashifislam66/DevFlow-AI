import jwt
from datetime import datetime, timedelta

SECRET_KEY = 'your_secret_key'

def check_auth(auth_header):
    if not auth_header:
        return False
    try:
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        if payload['exp'] < datetime.utcnow():
            return False
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False