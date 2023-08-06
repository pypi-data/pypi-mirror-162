from __future__ import annotations

from typing import TypeVar

from dependency_injector import containers
from dependency_injector.wiring import inject, Provide

from web_foundation.kernel import Isolate


class Worker(Isolate):
    _configured: bool

    def __init__(self, *args, **kwargs):
        self._configured = False

    @property
    def configured(self) -> bool:
        return self._configured

    @inject
    async def _init_resources(self, app_container=Provide["<container>"]):
        await app_container.init_resources()
        for service in app_container.app().services.values():
            service.worker = self
        pass

    def configure(self, name: str, debug=True, *args, **kwargs):
        self._configure_isolate(name, debug)
        self._configure(*args, **kwargs)
        self._configured = True

    def _configure(self, *args, **kwargs):
        pass

    def wire_worker(self, container: containers.DeclarativeContainer) -> None:
        raise NotImplementedError

    async def _run(self):
        raise NotImplementedError

    def _close(self):
        pass


GenWorker = TypeVar("GenWorker", bound=Worker)
