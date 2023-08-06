import asyncio
from dataclasses import dataclass
from typing import Coroutine, Callable, Dict, Type, List
from typing import TypeVar

import loguru
from aioprocessing import AioEvent, AioLock, AioQueue  # type: ignore
from loguru import logger


class IMessage:
    message_type: str = "__all__ "
    index: int
    sender: str

    def __init__(self):
        self.index = 0
        self.sender = "None"

    def __str__(self):
        return f"IMessage(id={self.index}, sender={self.sender})"


GenericIMessage = TypeVar("GenericIMessage", bound=IMessage, contravariant=True)


@dataclass
class IsolatePipes:
    queue: AioQueue
    event: AioEvent
    lock: AioLock

    async def write(self, msg: GenericIMessage):
        await self.queue.coro_put(msg)

    async def read(self) -> GenericIMessage:
        return await self.queue.coro_get()

    def empty(self):
        return self.queue.empty()


EventListener = Callable[[GenericIMessage], Coroutine]


class IChannel:
    read_timeout = 0.01
    pipes: IsolatePipes
    worker_name: str
    debug: bool
    consume_pipe: IsolatePipes
    produce_pipe: IsolatePipes
    _listeners: Dict[str, List[EventListener]]

    def __init__(self, isolate_name: str, debug: bool = False):
        self.worker_name = isolate_name
        self.debug = debug
        self._listeners = {}
        self.produce_pipe = IsolatePipes(AioQueue(), AioEvent(), AioLock())
        self.consume_pipe = IsolatePipes(AioQueue(), AioEvent(), AioLock())

    def __str__(self):
        return f"IChannel(name={self.worker_name})"

    async def produce(self, msg: IMessage):
        msg.sender = self.worker_name
        await self.produce_pipe.write(msg)

    async def listen_produce(self, callback: Callable[[GenericIMessage], Coroutine]):
        while True:
            if self.produce_pipe.empty():
                await asyncio.sleep(self.read_timeout)
            r: GenericIMessage = await self.produce_pipe.read()
            if self.debug:
                logger.info(
                    f"Channel {self.worker_name} send message: {r.message_type}")
            await callback(r)
            await asyncio.sleep(0.01)

    async def listen_consume(self):
        while True:
            if not self.consume_pipe.empty():
                r: IMessage = await self.consume_pipe.read()
                if self.debug:
                    logger.info(
                        f"Channel {self.worker_name} receive message: {r.message_type}")
                callbacks = self._listeners.get(r.message_type)
                if not callbacks:
                    continue
                for callback in callbacks:
                    asyncio.create_task(callback(r))
            await asyncio.sleep(0.01)

    def _add_event_listener(self, event_type: Type[IMessage] | str, callback: EventListener,
                            use_nested_classes: bool = False):
        if use_nested_classes and isinstance(event_type, str):
            raise AttributeError("Can't add_event_listener with use_nested_classes")

        def _add(event_name: str):
            nonlocal self
            nonlocal callback
            if event_name not in self._listeners:
                self._listeners[event_name] = []
            self._listeners[event_name].append(callback)

        if isinstance(event_type, str):
            _add(event_type)
        else:
            def _raise(cls_type):
                if not hasattr(cls_type, "message_type"):
                    raise AttributeError("Can't register listener cause message_type not found")

            if use_nested_classes:
                for cls in event_type.__subclasses__():
                    _raise(cls)
                    _add(cls.message_type)
            else:
                _raise(event_type)
                _add(event_type.message_type)

    def add_event_listener(self, event_type: List[Type[IMessage] | str] | Type[IMessage] | str,
                           callback: EventListener, use_nested_classes: bool = False):
        if isinstance(event_type, list):
            for i in event_type:
                self._add_event_listener(i, callback, use_nested_classes)
        else:
            self._add_event_listener(event_type, callback, use_nested_classes)

    def remove_event_listeners(self, event_type: Type[IMessage] | str):
        if isinstance(event_type, str):
            self._listeners.pop(event_type)
        else:
            self._listeners.pop(event_type.message_type)
