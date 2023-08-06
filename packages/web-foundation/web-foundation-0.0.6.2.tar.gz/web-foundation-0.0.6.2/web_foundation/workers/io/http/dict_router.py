from typing import Dict, Callable

from sanic import Sanic

from web_foundation.workers.io.http.ext_router import ExtRouter, RouteMethodConf, RouteConf


class DictRouter(ExtRouter):
    _router_conf: Dict
    chaining: Callable

    def __init__(self, routes_config: Dict, chaining: Callable):
        super().__init__()
        self.chaining = chaining
        self._router_conf = routes_config
        self.chains = []

    def apply_routes(self, app: Sanic, **kwargs):
        """
        If you want use chaining, please use partial(chain,validation_fnc=...,response_fabric=...)
        :param **kwargs:
        :param chaining:
        :return:
        """
        for app_route in self._router_conf.get("apps"):
            for endpoint, methods in app_route.get("endpoints").items():
                methods_confs = []
                for method_name, method_params in methods.items():
                    handler = method_params.get('handler')
                    protector = method_params.get("protector")
                    in_dto = method_params.get("in_dto")
                    out_dto = method_params.get("out_dto")
                    chain = self.chaining(
                        protector=protector,
                        in_struct=in_dto)(handler)
                    methods_confs.append(RouteMethodConf(method_name=method_name,
                                                         protector=protector,
                                                         in_dto=in_dto,
                                                         out_dto=out_dto,
                                                         handler=handler
                                                         ))
                    app.add_route(uri=endpoint, methods={method_name.upper()}, handler=chain)

                route = RouteConf(app_name=app_route.get("app_name"), path=endpoint, methods=methods_confs)
                self.chains.append(route)

        # warn(f"Can't find dto or handler in imported module, suppressed exception: {e.__str__()}")
