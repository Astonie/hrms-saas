from app.core.security import security_manager
from jose import jwt
import time

token = security_manager.create_access_token(subject='testuser')
print('token:', token)
claims = jwt.get_unverified_claims(token)
print('claims:', claims)
print('now:', int(time.time()))
print('exp:', claims.get('exp'))
print('exp datetime:', __import__('datetime').datetime.utcfromtimestamp(claims.get('exp')))
