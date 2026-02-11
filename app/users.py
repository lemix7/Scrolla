from app.db import User, get_user_db
import uuid
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models
from fastapi import Depends, Request
from dotenv import load_dotenv
import os
from fastapi_users.db import SQLAlchemyUserDatabase
from app.auth import auth_user

load_dotenv()


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):

    reset_password_token_secret = os.getenv('SECRET')
    verification_token_secret = os.getenv('SECRET')

    async def on_after_register(self, user: models.UP, request: Request | None = None) -> None:
        print(f'User{user.id} has registered')

    async def on_after_request_verify(self, user: models.UP, token: str, request: Request | None = None) -> None:
        print(
            f'Verification rquestedfor user {user.id} Verification token {token}')

    async def on_after_forgot_password(self, user: models.UP, token: str, request: Request | None = None) -> None:
        print(f'User {user.id} has forgot their password. Reset token: {token}')


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_user])

current_active_user = fastapi_users.current_user(active=True)
