async def some_handler(request):
    pass


async def some_protect(*asfasgasg,**kwargs):
    pass


class SomeDto:
    def __init__(self,*asfasgasg,**kwargs):
        pass


class SomeDto2:
    def __init__(self,*asfasgasg,**kwargs):
        pass


routes_dict = {
    "apps": [
        {
            "app_name": "ae_app",
            "endpoints": {
                "/ticket": {
                    "get": {
                        "handler": some_handler,
                    },
                    "post": {
                        "handler": some_handler,
                        "protector": some_protect,
                        "in_dto": SomeDto,
                        "out_dto": SomeDto2,
                    }
                }
            }
        }
    ]
}
