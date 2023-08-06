from dataclasses import dataclass
from typing import List, TypeVar, Tuple, Generic

from pydantic import BaseModel as PdModel
from tortoise.exceptions import IntegrityError, FieldError
from tortoise.queryset import QuerySet, MODEL

from web_foundation.app.errors.application.application import InconsistencyError
from web_foundation.app.infrastructure.database.models import GenericDbType
from web_foundation.app.infrastructure.database.utils import integrity_error_format
from web_foundation.workers.io.http.chaining import ProtectIdentity

EntityId = TypeVar("EntityId", bound=int)


@dataclass
class AccessProtectIdentity(Generic[GenericDbType], ProtectIdentity):
    pass


class DatabaseMiddleware:
    pass


class RelateDMW(DatabaseMiddleware):
    @staticmethod
    async def fetch_related(model: GenericDbType, query: QuerySet[MODEL],
                            fetch_fields: List[str] | None = None) -> QuerySet[MODEL]:
        if fetch_fields:
            for_select = {field for fk_field in model._meta.fk_fields for field in fetch_fields if
                          fk_field == field}
            for_prefetch = set(fetch_fields) - for_select
            if for_select:
                query = query.select_related(*for_select)
            if for_prefetch:
                query = query.prefetch_related(*for_prefetch)
        return query


class AccessDMW(DatabaseMiddleware):
    @staticmethod
    async def get_entity(model: GenericDbType,
                         entity_id: EntityId) -> GenericDbType:  # TODO TYPED USER
        entity = await model.get_or_none(id=entity_id)
        if not entity:
            raise InconsistencyError(message=f"{model.__name__} not found")  # type: ignore
        return entity

    @staticmethod
    async def create(model: GenericDbType, protection: AccessProtectIdentity, dto: PdModel,
                     **kwargs) -> GenericDbType:
        entity_kwargs = {field: value for field, value in dto.dict().items() if value is not None}
        try:
            entity = await model.create(**entity_kwargs)
        except IntegrityError as exception:
            raise integrity_error_format(exception)
        except ValueError as exception:
            raise InconsistencyError(exception)
        return entity

    @staticmethod
    async def read(model: GenericDbType, entity_id: EntityId, protection: AccessProtectIdentity,
                   fetch_fields: List[str] | None = None,
                   **kwargs) -> GenericDbType | None:
        query = model.filter(id=entity_id)
        if kwargs:
            query = query.filter(**kwargs)
        query = await RelateDMW.fetch_related(model, query, fetch_fields)
        entity = await query.first()
        return entity

    @staticmethod
    async def read_all(model: GenericDbType, protection: AccessProtectIdentity, limit: int = None, offset: int = None,
                       fetch_fields: List[str] = None,
                       **kwargs) -> Tuple[List[GenericDbType], int]:
        query = model.filter()
        if kwargs:
            if "order_by" in kwargs:
                query = query.order_by(kwargs.pop("order_by"))
            query = query.filter(**kwargs)

        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        query = await RelateDMW.fetch_related(model, query, fetch_fields)
        try:
            entities = await query
            query._limit = None
            query._offset = None
            total = await query.count()
        except FieldError:
            raise InconsistencyError(message="Incorrect filter")
        return entities, total

    @staticmethod
    async def update(model: GenericDbType, entity_id: EntityId, protection: AccessProtectIdentity, dto: PdModel,
                     **kwargs) -> GenericDbType:
        entity = await AccessDMW.get_entity(model, entity_id)
        entity_kwargs = {field: value for field, value in dto.dict().items() if value is not None}
        for field, value in entity_kwargs.items():
            setattr(entity, field, value)
        try:
            await entity.save(update_fields=list(entity_kwargs.keys()))
        except IntegrityError as exception:
            raise integrity_error_format(exception)
        except ValueError as exception:
            raise InconsistencyError(exception)
        return entity

    @staticmethod
    async def delete(model: GenericDbType, entity_id: EntityId, protection: AccessProtectIdentity,
                     **kwargs) -> GenericDbType:
        assert entity_id is not None
        entity = await AccessDMW.get_entity(model, entity_id)
        await entity.delete()
        return entity
