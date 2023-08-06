from typing import Iterable

from collections import defaultdict
from typing import Dict, FrozenSet

import loguru
from sanic import Sanic, response
from sanic.router import Route


def _compile_routes_needing_options(
        routes: Dict[str, Route]
) -> Dict[str, FrozenSet]:
    needs_options = defaultdict(list)
    # This is 21.12 and later. You will need to change this for older versions.
    for route in routes.values():
        if "OPTIONS" not in route.methods:
            needs_options[route.uri].extend(route.methods)

    return {
        uri: frozenset(methods) for uri, methods in dict(needs_options).items()
    }


def _options_wrapper(handler, methods):
    def wrapped_handler(request, *args, **kwargs):
        nonlocal methods
        return handler(request, methods)

    return wrapped_handler


async def options_handler(request, methods) -> response.HTTPResponse:
    resp = response.empty()
    _add_cors_headers(resp, methods)
    return resp


def setup_options(app: Sanic):
    app.router.reset()
    needs_options = _compile_routes_needing_options(app.router.routes_all)
    for uri, methods in needs_options.items():
        try:
            app.add_route(
                _options_wrapper(options_handler, methods),
                uri,
                methods=["OPTIONS"],
            )
        except:
            pass
    app.router.finalize()


def _add_cors_headers(response, methods: Iterable[str]) -> None:
    allow_methods = list(set(methods))
    if "OPTIONS" not in allow_methods:
        allow_methods.append("OPTIONS")
    headers = {
        "Access-Control-Allow-Methods": ",".join(allow_methods),
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Headers": (
            "origin, content-type, accept, "
            "authorization, x-xsrf-token, x-request-id"
        ),
    }
    response.headers.extend(headers)


def add_cors_headers(request, response):
    try:
        if request.method != "OPTIONS":
            if request.route and request.route.methods:
                methods = [method for method in request.route.methods]
                _add_cors_headers(response, methods)
    except:
        loguru.logger.warning("Fail add cors headers")
