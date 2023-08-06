import asyncio
from pathlib import Path

import loguru
from dependency_injector import providers, containers
from pydantic import BaseSettings
from tortoise import fields

from web_foundation.app.app import AppContainer
from web_foundation.app.events.base import AeEvent
from web_foundation.app.infrastructure.database.models import AbstractDbModel
from web_foundation.app.resources.database import DatabaseResource, DbConfig
from web_foundation.app.service import Service
from web_foundation.kernel import GenericIMessage
from web_foundation.workers.io.http.chaining import chain
from web_foundation.workers.io.http.routers.dict_router import DictRouter
from web_foundation.workers.io.http.routes_dict import routes_dict
from web_foundation.workers.io.rt_connection import RtConnection
from web_foundation.workers.io.sse.connection import SseRtMessage
from web_foundation.workers.io.worker import ServerConfig, create_io_workers, subscribe_worker_rt_callback


class AppConf(BaseSettings):
    app_name: str
    server: ServerConfig
    database: DbConfig


class AnyModel(AbstractDbModel):
    some_data = fields.TextField()


class TicketService(Service):
    def __init__(self):
        super().__init__()


@containers.copy(AppContainer)
class MyContainer(AppContainer):
    ticket_service = providers.Singleton(TicketService)
    database = providers.Resource(DatabaseResource, app_name="app_name",
                                  db_config=AppContainer.app_config.database,
                                  modules=[__name__])


async def resolve_send_event(conn: RtConnection, msg: GenericIMessage) -> SseRtMessage | None:
    loguru.logger.warning(conn)
    loguru.logger.warning(msg)
    return SseRtMessage(event_id=str(msg.index), event_name="new_event", data={"event": "aaaaaaa"})


async def main():
    container = MyContainer()
    container.app_config.from_pydantic(
        AppConf(app_name="first_app", server=ServerConfig(host="0.0.0.0", port=8000),
                database=DbConfig(
                    host="localhost",
                    port="5432",
                    database="aedb",
                    user="testuser",
                    password="Fedora132",
                    db_schema="ae",
                    with_migrations=False,
                    migrations_path=Path("")
                )))
    # router = YamlRouter(Path("../applyed_files/config/routing.yaml"), chain)
    router = DictRouter(routes_dict, chain)
    workers = create_io_workers(container.app_config.server(), router, workers_num=2)
    subscribe_worker_rt_callback(*workers, event_type=AeEvent, callback=resolve_send_event, use_nested_classes=True)

    # exexitor = TaskExecutor()
    # exexitor.configure("exec_worker")
    # container.app().add_worker(exexitor)

    container.app().add_worker(workers)
    loguru.logger.warning(container.app().dispatcher.channels)
    loguru.logger.warning([{i.channel.worker_name: i.channel._listeners} for i in container.app().workers.values()])
    # htpp_srv = HttpServer(container.app_config.server())
    # htpp_srv.configure("name", yaml_router=router, sock=socket)
    # htpp_srv_2 = HttpServer(container.app_config.server())
    # htpp_srv_2.configure("name2", yaml_router=router, sock=socket)
    #
    # container.app().add_worker(htpp_srv_2)
    container.app().add_service(container.ticket_service())
    container.app().wire_app(container)

    # container.wire_this()
    await container.app().run()


if __name__ == '__main__':
    asyncio.run(main())
