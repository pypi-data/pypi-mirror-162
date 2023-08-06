from dependency_injector.wiring import Provide, inject
from sanic import Request

from web_foundation.workers.io.http.chaining import InputContext

@inject
async def protect_user(r: Request,app_container=Provide["<container>"]):
    print(app_container)
    return {}
