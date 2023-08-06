from dependency_injector.wiring import Provide, inject
from sanic import Request


async def some_handler(request):
    return {}


@inject
async def some_protect(request: Request, app_container=Provide["<container>"]):
    print(app_container)
    return None


class SomeDto:
    def __init__(self, *asfasgasg, **kwargs):
        pass


class SomeDto2:
    def __init__(self, *asfasgasg, **kwargs):
        pass


routes_dict = {
    "apps": [
        {
            "app_name": "ae_app",
            "version_prefix": "/api/v",
            "endpoints": {
                "/ticket": {
                    "v14": {
                        "handler": some_handler,
                        "protector": some_protect,
                        "get": {},
                        "post": {
                            "handler": some_handler,
                            "protector": some_protect,
                        }
                    }
                }
            }
        }
    ]
}
