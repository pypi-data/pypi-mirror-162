# import pyyaml module
import traceback
from dataclasses import dataclass
from functools import partial
from importlib import import_module
from pathlib import Path
from typing import List, Type, Dict, Callable
from warnings import warn

import yaml
from pydantic import BaseModel
from sanic import Sanic
from yaml.loader import SafeLoader

from web_foundation.app.errors.io.routing import YamlRouterLoadFileError
from web_foundation.workers.io.http.chaining import Protector, HandlerType
from web_foundation.workers.io.http.routers.ext_router import ExtRouter


@dataclass
class RouteMethodConf:
    method_name: str
    protector_path: str | None
    in_dto: str | None
    out_dto: str | None


@dataclass
class RouteConf:
    app_name: str
    scope: str
    path: str
    methods: List[RouteMethodConf]
    handler_path: str

    def dict_(self):
        return {"app_name": self.app_name, "scope": self.scope, "path": self.path}


@dataclass
class ImportedRouteMethodConf:
    method_name: str
    protector: Protector | None
    in_dto: Type[BaseModel] | None
    out_dto: Type[BaseModel] | None


@dataclass
class ImportedRouteConf:
    app_name: str
    scope: str
    path: str
    methods: List[ImportedRouteMethodConf]
    handler: HandlerType


class YamlRouter(ExtRouter):
    routes_confs: List[RouteConf]
    _routes_config: Path
    _route_protectors: Dict[str, Dict[str, str]]
    protectors: Dict[str, partial[Protector]]
    chains: List[ImportedRouteConf]
    chaining: Callable

    def __init__(self, routes_config: Path, chaining: Callable):
        super().__init__()
        self.chaining = chaining  # type: ignore
        self._routes_config = routes_config
        self._route_protectors = {}
        self.protectors = {}
        self.chains = []
        self.routes_confs = self._parce_file()

    def _parce_file(self) -> List[RouteConf]:
        try:
            with open(self._routes_config, 'r') as conf_f:
                yml = yaml.load(conf_f, Loader=SafeLoader)
                for app_name, data in yml["apps"].items():
                    if data["routes"].get("protectors"):
                        for protector_name, pr_settings in data["routes"].get("protectors").items():
                            pr_settings.update({"app_name": app_name})
                            self._route_protectors.update({protector_name: pr_settings})
                    endpoints = data["routes"]["endpoints"]
                    routes = []
                    for scope, params in endpoints.items():
                        base_protector = params.get("protector")
                        methods = []
                        for method, cfg in params.get("methods").items():
                            protector = cfg.get("protector")
                            if protector is not None:
                                protector = base_protector
                            methods.append(
                                RouteMethodConf(method_name=method, protector_path=protector,
                                                in_dto=cfg.get("in-dto"), out_dto=cfg.get("out-dto"))
                            )
                        route_cfg = RouteConf(app_name=app_name,
                                              scope=scope,
                                              path=params["path"],
                                              handler_path=params["handler"],
                                              methods=methods
                                              )
                        routes.append(route_cfg)
                    for pr_name, pr_settings in self._route_protectors.items():
                        app_name = pr_settings.pop("app_name")
                        fnc_name = pr_settings.pop("fnc")
                        if not fnc_name:
                            continue
                        splits_name = fnc_name.split(".")
                        module_name = ".".join([app_name, *splits_name[:-1]])
                        fnc = getattr(import_module(module_name), splits_name[-1])
                        self.protectors.update({pr_name: partial(fnc, **pr_settings)})
                return routes
        except Exception as e:
            raise YamlRouterLoadFileError(e)

    def _get_importable(self, app_name: str, scope: str, kind: str, path: str):
        if not path:
            return None
        module = import_module(".".join([app_name, "api", scope, "handlers"]))
        return getattr(module, path)

    def apply_routes(self, app: Sanic):
        """
        If you want use chaining, please use partial(chain,validation_fnc=...,response_fabric=...)
        :param chaining:
        :return:
        """
        try:
            for route in self.routes_confs:
                importer = partial(self._get_importable, app_name=route.app_name, scope=route.scope)
                imported_conf = ImportedRouteConf(handler=importer(path=route.handler_path, kind="handlers"),
                                                  **route.dict_(), methods=[])
                for method in route.methods:
                    imported_method = ImportedRouteMethodConf(method_name=method.method_name,
                                                              protector=self.protectors.get(method.protector_path),
                                                              in_dto=importer(path=method.in_dto, kind="dtos"),
                                                              out_dto=importer(path=method.out_dto, kind="dtos"),
                                                              )
                    imported_conf.methods.append(imported_method)
                    handler = self.chaining(
                        protector=imported_method.protector,
                        in_struct=imported_method.in_dto)(imported_conf.handler)
                    app.add_route(uri=route.path, methods={method.method_name.upper()}, handler=handler)
                self.chains.append(imported_conf)
        except ImportError as e:
            warn(f"Can't import from config path, suppressed exception: {e.__str__()}")
        except AttributeError as e:
            traceback.print_tb(e.__traceback__)
            warn(f"Can't find dto or handler in imported module, suppressed exception: {e.__str__()}")

#
# r = set_to_pipline(acc.uri)(wraps(target)(partial(target)))
