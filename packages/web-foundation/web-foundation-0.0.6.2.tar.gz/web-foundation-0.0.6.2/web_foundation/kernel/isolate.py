import asyncio
from abc import ABCMeta, abstractmethod
from asyncio import Future

from aioprocessing import AioProcess
from web_foundation.kernel.channel import IChannel


class Isolate(metaclass=ABCMeta):
    debug: bool
    _name: str
    _channel: IChannel
    _proc: AioProcess
    _created = False

    @property
    def name(self):
        return self._name

    @property
    def created(self):
        return self._created

    def _configure_isolate(self, name: str, debug=True):
        self.debug = debug
        self._name = name
        self._proc = AioProcess(target=self._startup)
        self._channel = IChannel(self._name, debug=debug)
        self._created = True

    @abstractmethod
    async def _run(self):
        pass

    @abstractmethod
    def _close(self, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        self._close(*args, **kwargs)

    def _startup(self):
        asyncio.run(self._run())

    async def _exec(self):
        self._proc.start()

    def perform(self) -> Future:
        if not self._created:
            raise AttributeError("Call configure_isolate() before start perform")
        return asyncio.ensure_future(self._exec())

    @property
    def channel(self) -> IChannel:
        return self._channel

    @property
    def pid(self) -> int:
        return self._proc.pid

    @property
    def process(self) -> AioProcess:
        return self._proc

    def __str__(self):
        return f"{self.__class__.__name__}({self.name}) on pid: {self.pid}"
