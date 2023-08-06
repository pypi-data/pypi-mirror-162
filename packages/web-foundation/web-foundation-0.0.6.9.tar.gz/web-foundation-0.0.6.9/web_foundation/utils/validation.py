from typing import Type

from sanic import Request
from pydantic import ValidationError as PdValidationError, BaseModel as PdModel

from web_foundation.app.errors.application.application import ValidationError


def validate_dto(dto_cls: Type[PdModel] | None,request: Request) -> PdModel | None:
    if not dto_cls:
        return None
    try:
        dto = dto_cls(**request.json)
        return dto
    except PdValidationError as ex:
        failed_fields = ex.errors()
        fields = [field["loc"][-1] for field in failed_fields]
        commment_str = "Some of essential params failed : " + ", ".join(
            [field["loc"][-1] + " - " + field["msg"] for field in failed_fields])
        message = commment_str
        context = {
            "fields": fields,
            "comment": commment_str
        }
        raise ValidationError(message=message,
                              context=context)


def dto_validation_error_format(exeption: PdValidationError):
    failed_fields = exeption.errors()
    commment_str = "Some of essential params failed : " + ", ".join(
        [str(field["loc"][-1]) + " - " + field["msg"] for field in failed_fields])
    return commment_str
