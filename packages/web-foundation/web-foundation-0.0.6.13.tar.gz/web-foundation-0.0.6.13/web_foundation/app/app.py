from __future__ import annotations
import asyncio
import json
from asyncio import Future
from pathlib import Path
from typing import List, Type, TypeVar, Generic, Dict, Any

from dependency_injector import providers, containers, resources
from dependency_injector.wiring import inject, Provide
from pydantic import BaseSettings

from web_foundation.kernel.dispatcher import IDispatcher
from web_foundation.app.resources.cache.cache import AppCache
from web_foundation.app.resources.cache.memory import InMemoryCache
from web_foundation.app.service import Service
from web_foundation.kernel.logger import setup_loggers, LoggerSettings
from web_foundation.workers.worker import GenWorker

AppConfig = TypeVar("AppConfig", bound=BaseSettings)


class App(Generic[AppConfig, GenWorker]):
    config: AppConfig
    name: str
    workers: Dict[str, GenWorker]
    services: Dict[str, Service]
    dispatcher: IDispatcher
    debug: bool  # type: ignore

    def __init__(self, config: providers.Configuration, debug: bool = False):
        self.debug = debug
        self.name = config.get("app_name")
        self.config = config
        self.workers = {}
        self.services = {}
        self.dispatcher = IDispatcher()

    @inject
    async def _before_app_run(self, app_container: AppContainer = Provide["<container>"]):
        await app_container.init_resources()
        await self.before_app_run(app_container)
        await app_container.shutdown_resources()

    async def before_app_run(self, container):
        pass

    def _add_worker(self, worker: GenWorker):
        if not worker.configured:
            raise RuntimeError("Worker not configured")
        worker.debug = self.debug
        self.dispatcher.reg_worker(worker)
        self.workers.update({worker.name: worker})

    def add_worker(self, worker: GenWorker | List[GenWorker]):
        """
        Set isolate to app and set isolate debug and name
        :param worker: isolate to apply
        :return: None
        """
        if isinstance(worker, list):
            for w in worker:
                self._add_worker(w)
        else:
            self._add_worker(worker)

    def add_service(self, service: Service):
        self.services.update({service.__class__.__name__: service})

    def find_worker_by_pid(self, pid: int):
        for worker in self.workers.values():
            if worker.pid == pid:
                return worker

    def wire_app(self, container: AppContainer):
        container.wire(modules=[self.__module__])
        for worker in self.workers.values():
            container.wire(modules=[worker.__module__])
            worker.wire_worker(container)

    def perform(self) -> List[Future[Any]]:
        """
        Call performs from isolates and return all isolates Futures
        :return: None
        """
        return [worker.perform() for worker in self.workers.values()]

    async def run(self):
        await self._before_app_run()
        """
        Func to run app manually (without Runner)
        :return: None
        """
        return await asyncio.wait(self.perform() + self.dispatcher.preform())


def load_config(conf_path: Path, config_model: Type[AppConfig]) -> AppConfig:
    """
    Load app config to user in
    :param conf_path:
    :param config_model: BaseModel to cast json file to pydantic
    :return: None
    """
    with open(conf_path, "r") as _json_file:
        conf = config_model(**json.loads(_json_file.read()))
        return conf


class AppContainer(containers.DeclarativeContainer):
    debug = True
    app_config = providers.Configuration()
    app = providers.Dependency(instance_of=App, default=providers.Singleton(App, config=app_config, debug=debug))
    cache = providers.Dependency(instance_of=AppCache, default=providers.Singleton(InMemoryCache))
    """
    Please pass here your database or any another resource in nested container
    """

    def apply_resource(self, name: str, resource: Type[resources.AsyncResource], **kwargs):
        setattr(self, name, providers.Resource(resource, app_name=self.app_config.get("app_name"), **kwargs))
