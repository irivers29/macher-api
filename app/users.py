from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.authentication import AuthenticationBackend, CookieTransport, JWTStrategy
from app.models import get_user_db, User
from typing import Optional


SECRET = "verysecuresecret"


class UserManager(UUIDIDMixin, BaseUserManager):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        # todo: send email with reset password link
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(
            f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


cookie_transport = CookieTransport(
    cookie_httponly=True, cookie_secure=False)


def get_jwt_strategy():
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt", get_strategy=get_jwt_strategy, transport=cookie_transport)

fastapi_users = FastAPIUsers(
    get_user_manager=get_user_manager, auth_backends=[auth_backend])

active_user = fastapi_users.current_user(active=True, verified=True)
