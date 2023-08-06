import inspect
import re
from typing import Dict, Callable, Type
from pydantic import BaseModel as PdModel

import sanic_ext
from sanic import Sanic
from sanic_ext.extensions.openapi.builders import SpecificationBuilder, OperationStore

from web_foundation.workers.io.http.routers.ext_router import ExtRouter, RouteMethodConf, RouteConf


def get_definition_with_correct_name(definitions: Dict) -> Dict:
    _definitions = {}
    for defin, _schema in definitions.copy().items():
        if "." in defin:
            _definitions[defin.split(".")[-2]] = _schema
        else:
            _definitions[defin] = _schema
    return _definitions


def get_model_schema(model: Type[PdModel]):
    """ Create schema from pydantic model and add all references to OpenAPI schemas """
    schema = model.schema(ref_template="#/components/schemas/{model}")
    components = {}
    if "definitions" in schema:
        definitions = get_definition_with_correct_name(schema.pop("definitions"))
        components.update(definitions)
    components.update({model.__name__: schema})
    spec = SpecificationBuilder()
    for component_name, component in components.items():
        spec._components["schemas"].update({component_name: component})
    return schema


def add_openapi_spec(uri:str, method_name: str, func:Callable, handler: Callable,
                     in_dto: Type[PdModel], out_dto: Type[PdModel]):
    # --- add query args ---#
    func_text = inspect.getsource(func)
    func_query_args = re.findall(r"request.args.get\(\"(\w*)\"\)", func_text)
    if func_query_args:
        for func_arg in func_query_args:
            handler = sanic_ext.openapi.parameter(func_arg)(handler)
    # --- add request body ---#
    if in_dto:
        if issubclass(in_dto, PdModel):
            schema = get_model_schema(in_dto)
            OperationStore()[handler].requestBody = {"content": {"application/json": {'schema': schema}}}
    # --- add response ---#
    if out_dto:
        if issubclass(out_dto, PdModel):
            schema = get_model_schema(out_dto)
            OperationStore()[handler].responses[200] = {"content": {"application/json": {'schema': schema}}}
    # --- add tag ---#
    handler = sanic_ext.openapi.tag(uri.split("/")[1].capitalize())(handler)  # first path word

    # --- decription --- #
    # f = sanic_ext.openapi.description("hujkiikasdf;awerfl;jkasdfklj;asdfjkl;")(handler)
    # f = sanic_ext.openapi.summary("l;kasdjllww")(handler)

    # --- set operation id --- #
    handler = sanic_ext.openapi.operation(f"{method_name}~{uri}")(handler)
    return handler


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
                    target_func = method_params.get('handler')
                    protector = method_params.get("protector")
                    in_dto = method_params.get("in_dto")
                    out_dto = method_params.get("out_dto")
                    chain = self.chaining(
                        protector=protector,
                        in_struct=in_dto)(target_func)
                    methods_confs.append(RouteMethodConf(method_name=method_name,
                                                         protector=protector,
                                                         in_dto=in_dto,
                                                         out_dto=out_dto,
                                                         handler=target_func
                                                         ))
                    chain = add_openapi_spec(uri=endpoint, method_name=method_name, func=target_func,
                                             handler=chain, in_dto=in_dto, out_dto=out_dto)
                    app.add_route(uri=endpoint, methods={method_name.upper()}, handler=chain)

                route = RouteConf(app_name=app_route.get("app_name"), path=endpoint, methods=methods_confs)
                self.chains.append(route)

        # warn(f"Can't find dto or handler in imported module, suppressed exception: {e.__str__()}")
