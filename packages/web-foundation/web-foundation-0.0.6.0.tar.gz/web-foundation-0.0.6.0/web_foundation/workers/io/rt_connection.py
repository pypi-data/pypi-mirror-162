from __future__ import annotations

import asyncio
from asyncio import Task
from typing import Generic, Any, Callable, Coroutine

import loguru
from loguru import logger

from web_foundation.kernel import GenericIMessage
from web_foundation.workers.io.http.chaining import InputContext


class RtMessage:

    def _prepare(self, *args, **kwargs) -> str | bytes:
        raise NotImplementedError

    @property
    def to_sent(self) -> str | bytes:
        return self._prepare()

    @classmethod
    def ping_message(cls):
        raise NotImplementedError


class WriteableObj:
    obj: Any

    def __init__(self, obj: Any):
        self.obj = obj

    async def write(self, message: Any) -> None:
        pass


class RtConnection(Generic[GenericIMessage]):
    debug: bool
    ping_timeout: float
    listen_timeout: float
    writeable: WriteableObj
    input_ctx: InputContext
    _last_event_id: int
    _ping_task: Task
    _ping_enable: bool
    _on_disconnect: Callable[[], Coroutine]

    def __init__(self, input_ctx: InputContext, writeable: WriteableObj, debug: bool = True, ping_enable: bool = True,
                 ping_timeout=None,
                 listen_timeout=None):
        self.writeable = writeable
        self.input_ctx = input_ctx
        self.debug = debug
        self._ping_enable = ping_enable
        self.ping_timeout = ping_timeout if ping_timeout else 5
        self.listen_timeout = listen_timeout if listen_timeout else 0.1
        self._last_event_id = 0

    def _ping_msg(self) -> str | bytes:
        raise NotImplementedError

    async def _ping(self):
        while True:
            await self.writeable.write(self._ping_msg())
            if self.debug:
                logger.debug(f"Sent ping to {self.input_ctx.request.ip}")
            await asyncio.sleep(self.ping_timeout)

    async def freeze_request(self, on_disconnect: Callable[[], Coroutine]):
        self._on_disconnect = on_disconnect
        await self._ping()

    async def send_after_call(self, event: GenericIMessage, resolve_callback: RtEventCallback):
        msg = await resolve_callback(self, event)
        if msg:
            await self.writeable.write(msg.to_sent)

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        loguru.logger.warning("as[gjasbngkasngjansg")
        await self._on_disconnect()
        if self.debug:
            logger.debug(
                f"RtConnection({self.__class__.__name__}) on {self.input_ctx.request.ip} disconnected, ping task canceled")

    def _close_condition(self) -> bool:
        raise NotImplementedError

    @classmethod
    async def accept_connection(cls, input_ctx: InputContext,
                                ping_enable: bool = True,
                                ping_timeout=None,
                                listen_timeout=None,
                                debug: bool = True) -> RtConnection:
        raise NotImplementedError

    @classmethod
    async def _construct_writable(cls, input_ctx: InputContext, *args, **kwargs) -> WriteableObj:
        raise NotImplementedError


RtEventCallback = Callable[[RtConnection, GenericIMessage], Coroutine[Any, Any, RtMessage | None]]

#
# async def stream_queued_events(self, resolve_callback: ResolvedCallback) -> None:
#
#     self._response = await self.input_ctx.request.respond(content_type="text/event-stream")
#     ping_task = self.input_ctx.request.app.loop.create_task(_ping(self.ping_timeout))
#     while True:
#         if not self._response.stream:
#             ping_task.cancel()
#             print(f"Sse on {self.input_ctx.request.ip} disconnected, ping task canceled")
#             break
#         if not self.connection_queue.empty():
#             resolved = await resolve_callback(self, await self.connection_queue.get())
#             if resolved.disconnect:
#                 break
#             if resolved.event_data and resolved.event_name != "":
#                 ev_payload = SseProto(event_id=str(self._last_event_id), event_name=resolved.event_name,
#                                       data=resolved.event_data).to_send
#                 await self._response.send(ev_payload.encode())
#                 self._last_event_id += 1
#         await asyncio.sleep(self.listen_timeout)
