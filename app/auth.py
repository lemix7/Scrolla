from fastapi_users.authentication import BearerTransport, JWTStrategy, AuthenticationBackend
from dotenv import load_dotenv
import os

load_dotenv()

bearer_transport = BearerTransport(tokenUrl='auth/jwt/login')


def jwt_strategy():
    return JWTStrategy(secret=os.getenv('SECRET'), lifetime_seconds=3600)


auth_user = AuthenticationBackend(name='jwt',
                                  transport=bearer_transport, get_strategy=jwt_strategy)
