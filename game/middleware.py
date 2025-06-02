from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from accounts.models import Player
import jwt
from django.conf import settings

@database_sync_to_async
def get_user(user_id):
    try:
        return Player.objects.get(id=user_id)
    except Player.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token_list = params.get("token")
        user = AnonymousUser()

        if token_list:
            token = token_list[0]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = payload.get("user_id")
                if user_id:
                    user = await get_user(user_id)
            except Exception as e:
                print("JWT decode error:", e)
                user = AnonymousUser()

        scope["user"] = user
        return await super().__call__(scope, receive, send)