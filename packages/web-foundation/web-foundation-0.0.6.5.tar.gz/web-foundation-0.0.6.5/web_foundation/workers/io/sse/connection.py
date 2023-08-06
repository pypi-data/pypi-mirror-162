from __future__ import annotations

import io
import json
from dataclasses import dataclass, field
from typing import Any
from typing import Dict

from sanic.response import BaseHTTPResponse

from web_foundation.workers.io.http.chaining import InputContext
from web_foundation.workers.io.rt_connection import WriteableObj, RtConnection, RtMessage


@dataclass
class SseRtMessage(RtMessage):
    _SEPARATOR = "\r\n"
    event_name: str
    event_id: str | None = field(default=None)
    data: Dict | None = field(default=None)
    retry: int | None = field(default=None)

    def _prepare(self, *args, **kwargs) -> str | bytes:
        buffer = io.StringIO()
        buffer.write('event: ' + self.event_name + self._SEPARATOR)
        if self.event_id:
            buffer.write('id: ' + self.event_id + self._SEPARATOR)
        if self.retry:
            buffer.write('retry: ' + str(self.retry) + self._SEPARATOR)
        else:
            buffer.write("retry: " + "0" + self._SEPARATOR)
        if self.data:
            buffer.write('data: ' + json.dumps(self.data))
        else:
            buffer.write('data: ')
        buffer.write("\r\n\r\n")
        return buffer.getvalue()

    @classmethod
    def ping_message(cls):
        return cls(event_id="0", event_name="ping").to_sent


class WriteableSse(WriteableObj):
    obj: BaseHTTPResponse

    def __init__(self, obj: BaseHTTPResponse):
        super().__init__(obj)

    async def write(self, message: Any) -> None:
        await self.obj.send(message)


class SseRtConnection(RtConnection):
    writeable: WriteableSse

    def _ping_msg(self) -> str | bytes:
        return SseRtMessage.ping_message()

    @classmethod
    async def accept_connection(cls, input_ctx: InputContext, ping_enable: bool = True, ping_timeout=None,
                                listen_timeout=None, debug: bool = True) -> SseRtConnection:
        writable = await cls._construct_writable(input_ctx)
        instance = cls(input_ctx, writable, ping_enable, ping_timeout, listen_timeout, debug)
        return instance

    @classmethod
    async def _construct_writable(cls, input_ctx: InputContext, *args, **kwargs) -> WriteableSse:
        _response = await input_ctx.request.respond(content_type="text/event-stream")
        return WriteableSse(_response)

    def _close_condition(self) -> bool:
        if not self.writeable.obj.stream:
            return True
        else:
            return False

# class SseConnection(Generic[GenericIMessage]):
#     ping_timeout: float
#     listen_timeout: float
#     input_ctx: InputContext
#     connection_queue: Queue[GenericIMessage]
#     _last_event_id: int
#     _response: HTTPResponse
#     _alive: bool
#
#     def __init__(self, input_ctx, connection_queue: Queue[GenericIMessage], ping_timeout=None, listen_timeout=None):
#         self.input_ctx = input_ctx
#         self.connection_queue = connection_queue
#         self.ping_timeout = ping_timeout if ping_timeout else 5
#         self.listen_timeout = listen_timeout if listen_timeout else 0.1
#         self._last_event_id = 0
#
#     async def stream_queued_events(self, resolve_callback: ResolvedCallback) -> None:
#         async def _ping(ping_timeout: float):
#             ping_event = await SseProto.ping_message()
#             while True:
#                 if not self._response.stream:
#                     return
#                 await asyncio.sleep(ping_timeout)
#                 loguru.logger.warning("PINFFFFFF")
#                 await self._response.send(ping_event)
#
#         self._response = await self.input_ctx.request.respond(content_type="text/event-stream")
#         ping_task = self.input_ctx.request.app.loop.create_task(_ping(self.ping_timeout))
#         while True:
#             if not self._response.stream:
#                 ping_task.cancel()
#                 print(f"Sse on {self.input_ctx.request.ip} disconnected, ping task canceled")
#                 break
#             if not self.connection_queue.empty():
#                 resolved = await resolve_callback(self, await self.connection_queue.get())
#                 if resolved.disconnect:
#                     break
#                 if resolved.event_data and resolved.event_name != "":
#                     ev_payload = SseProto(event_id=str(self._last_event_id), event_name=resolved.event_name,
#                                           data=resolved.event_data).to_send
#                     await self._response.send(ev_payload.encode())
#                     self._last_event_id += 1
#             await asyncio.sleep(self.listen_timeout)


# ResolvedCallback = Callable[[SseConnection, GenericIMessage], Coroutine[Any, Any, SseResolved]]
