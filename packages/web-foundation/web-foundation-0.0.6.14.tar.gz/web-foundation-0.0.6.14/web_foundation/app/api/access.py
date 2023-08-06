from typing import List

from sanic import json
from sanic.exceptions import NotFound
import json as py_json

from web_foundation.app.infrastructure.database.middleware import AccessDMW
from web_foundation.app.infrastructure.database.models import AbstractDbModel
from web_foundation.workers.io.http.chaining import InputContext


async def exec_access(inc: InputContext,
                      model: AbstractDbModel,
                      fetch_fields: List[str] = None
                      ):
    """
    Access to models
    """
    match inc.request.method:
        case "GET":
            kwargs = inc.r_kwargs
            entity_id = kwargs.pop("entity_id", None)
            if entity_id is None:
                limit = inc.request.args.get("limit")
                offset = inc.request.args.get("offset")
                limit = int(limit) if limit and limit.isdigit() else 100
                offset = int(offset) if offset and offset.isdigit() else None
                # order_by = inc.request.args.get("order_by")  # for openapi. Variable forwarded to read_all in kwargs
                for ar, val in inc.request.args.items():
                    if ar in ["limit", "offset"]:
                        continue
                    val = val[0]
                    if val.lower() == 'false':
                        val = False
                    elif val.lower() == 'true':
                        val = True
                    elif val.isdigit():
                        val = int(val)
                    elif "." in val and val.replace('.', '').isdigit():
                        val = float(val)
                    elif val.startswith("["):
                        val = py_json.loads(val)
                    kwargs[ar] = val

                retrieved_all, total = await AccessDMW.read_all(model, inc.identity, limit, offset,
                                                                fetch_fields=fetch_fields, **kwargs)
                res = [await model.values_dict() for model in retrieved_all]
                return res
            retrieved = await AccessDMW.read(model, entity_id, inc.identity, fetch_fields=fetch_fields, **kwargs)
            if retrieved:
                result = await retrieved.values_dict()
                return result
            else:
                raise NotFound()

        case "POST":
            assert inc.dto
            retrieved = await AccessDMW.create(model, inc.identity, inc.dto, **inc.r_kwargs)
            if isinstance(retrieved, list):
                return [await i.values_dict() for i in retrieved]
            return await retrieved.values_dict()

        case "PATCH":
            assert inc.dto
            entity_id = inc.r_kwargs.pop("entity_id")
            assert entity_id
            retrieved = await AccessDMW.update(model, entity_id, inc.identity, inc.dto, **inc.r_kwargs)
            return await retrieved.values_dict()

        case "DELETE":
            entity_id = inc.r_kwargs.pop("entity_id")
            assert entity_id
            retrieved = await AccessDMW.delete(model, entity_id, inc.identity, **inc.r_kwargs)
            return await retrieved.values_dict()