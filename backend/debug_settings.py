from app.core.config import settings
print('jwt_access_token_expire_minutes =', settings.jwt_access_token_expire_minutes)
print('jwt_refresh_token_expire_days =', settings.jwt_refresh_token_expire_days)
print('environment =', settings.environment)
print('jwt_secret_key length =', len(settings.jwt_secret_key) if settings.jwt_secret_key else None)
