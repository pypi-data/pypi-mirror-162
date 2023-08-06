from sanic import Request

from web_foundation.workers.io.http.chaining import InputContext


async def protect_user(r: Request, *args, **kwargs):
    return {}
