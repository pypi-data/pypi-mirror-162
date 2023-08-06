import importlib
import os
from pathlib import Path
from types import ModuleType
from typing import List, Optional, Dict

from dependency_injector import resources
from loguru import logger
from pydantic import BaseModel as PDModel
from tortoise import Tortoise, BaseDBAsyncClient, connections


class DbConfig(PDModel):
    host: str
    port: str
    database: str
    user: str
    password: str
    db_schema: str
    with_migrations: bool
    migrations_path: Path


class DatabaseResource(resources.AsyncResource):
    modules: List[str]
    connection: BaseDBAsyncClient | None
    _app_name: str

    def _get_connection_setting(self) -> dict:
        if self.db_conf.get("with_migrations"):
            self.modules.append("aerich.models")
        to_discover = [importlib.import_module(i) for i in self.modules]
        return {
            'connections': {
                # Dict format for connection
                f'{self._app_name}_default': {
                    'engine': self.engine,
                    'credentials': {
                        'host': self.db_conf['host'],
                        'port': self.db_conf['port'],
                        'user': self.db_conf["user"],
                        'password': self.db_conf["password"],
                        'database': self.db_conf["database"],
                        'schema': self.db_conf["db_schema"],
                        'minsize': 1,
                        'maxsize': 5,
                    }
                }
            },
            'apps': {
                f'{self._app_name}': {
                    'models': to_discover,
                    'default_connection': f'{self._app_name}_default',
                }
            },
            'use_tz': False,
            'timezone': 'UTC'
        }

    async def fill_db_data(self):
        pass

    async def init(self, app_name: str, db_config: Dict, modules: List[str],
                   engine: str = 'tortoise.backends.asyncpg') -> BaseDBAsyncClient:
        super().__init__()
        self._app_name = app_name
        self.db_conf = db_config
        self.modules = modules
        self.connection = None
        self.engine = engine
        await Tortoise.init(config=self._get_connection_setting())
        return Tortoise.get_connection(f'{self._app_name}_default')

    async def shutdown(self, resource: Optional[Tortoise]) -> None:
        await self.close()

    @property
    def conn(self) -> BaseDBAsyncClient:
        if not self.connection:
            self.connection = Tortoise.get_connection(connection_name=f'{self._app_name}_default')
        return self.connection

    async def _migrations(self, schema_exists: bool, command):
        path_exists = os.path.exists(os.path.join(os.getcwd(), self.db_conf["migrations_path"]))

        if not path_exists and not schema_exists:
            await self.create_schema(False)
            await command.init()
            await command.init_db(safe=True)
        elif not schema_exists:
            await self.create_schema(False)
            await command.init()
            await command.upgrade()
        else:
            await command.init()
        logger.info(f"Apply migrations from {self.db_conf['migrations_path']}")
        await command.migrate()
        await command.upgrade()

    async def configure_db(self):
        row_count, rows = await self.conn.execute_query(
            f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = {self.db_conf.schema}")
        schema_exists = True if row_count else False
        if self.db_conf.with_migrations:
            if not self.db_conf['migrations_path']:
                raise ValueError("Field needmigrations_aeirch in db config set to false, can't migrate")
            from aerich import Command
            command = Command(tortoise_config=self._get_connection_setting(), app=self._app_name,
                              location=self.db_conf['migrations_path'])
            await self._migrations(schema_exists, command)
        if not schema_exists:
            await self.fill_db_data()

    async def close(self):
        await connections.close_all()

    async def create_schema(self, generate_schemas: bool = True):
        await self.conn.execute_script(f"CREATE SCHEMA IF NOT EXISTS {self.db_conf['schema']};")
        if generate_schemas:
            await Tortoise.generate_schemas()
