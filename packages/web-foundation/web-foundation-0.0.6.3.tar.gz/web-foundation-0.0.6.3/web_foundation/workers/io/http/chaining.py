from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Type, Coroutine, TypeVar, Generic
from typing import Union, Dict, List

from pydantic import BaseModel as PdModel
from sanic import Request, json, HTTPResponse

from web_foundation.utils.validation import validate_dto

DtoType = TypeVar("DtoType", bound=PdModel)


@dataclass
class ProtectIdentity():
    pass


ProtectIdentityType = TypeVar("ProtectIdentityType", bound=ProtectIdentity)


@dataclass
class InputContext(Generic[DtoType, ProtectIdentityType]):
    request: Request
    dto: DtoType | None
    identity: ProtectIdentity | None
    r_kwargs: Dict


Protector = Callable[[Request], Coroutine[Any, Any, ProtectIdentityType | None]]
DtoValidator = Callable[[Type[DtoType], Request], PdModel]
HandlerType = Callable[[InputContext], Coroutine[Any, Any, HTTPResponse]]

JSON = Union[Dict[str, Any], List[Any], int, str, float, bool, Type[None]]
TypeJSON = Union[Dict[str, 'JSON'], List['JSON'], int, str, float, bool, Type[None]]


async def protect(request: Request) -> ProtectIdentity | None:
    return None


def chain(protector: Protector = protect,
          in_struct: Type[PdModel] | None = None,
          validation_fnc: DtoValidator = validate_dto,
          response_fabric: Callable[[TypeJSON], HTTPResponse] = json):
    def called_method(target: HandlerType):
        @wraps(target)
        async def f(*args, **kwargs):
            req: Request = args[0]
            prot_identity = await protector(req) if protector else None
            if in_struct:
                validated = validation_fnc(in_struct, req)
            else:
                validated = None
            incoming = InputContext(req, validated, prot_identity, kwargs)
            ret_val = await target(incoming)
            return response_fabric(ret_val)

        return f

    return called_method


async def any_protect():
    pass


class Str(PdModel):
    name: str


async def handler(inc: InputContext):
    return {}
