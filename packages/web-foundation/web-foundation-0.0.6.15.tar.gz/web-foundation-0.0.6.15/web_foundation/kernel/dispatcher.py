import asyncio
from asyncio import Task, Future
from typing import Dict, List, Any

import loguru

from web_foundation.kernel import IChannel, GenericIMessage
from web_foundation.workers.worker import GenWorker


class IDispatcher:
    debug: bool = True
    channels: Dict[str, IChannel]
    _msg_global_index: int

    def __init__(self):
        self._msg_global_index = 0
        self.channels = {}

    def reg_worker(self, worker: GenWorker):
        self.channels.update({worker.name: worker.channel})

    async def on_channel_sent(self, msg: GenericIMessage):
        self._msg_global_index += 1
        msg.index = self._msg_global_index
        asyncio.create_task(self.broadcast(msg))

    async def broadcast(self, msg: GenericIMessage):
        for ch in self.channels.values():
            if self.debug:
                loguru.logger.debug(f"Sent {msg} to {ch.worker_name}")
            await ch.consume_pipe.write(msg)

    def preform(self) -> List[Future[Any]]:
        tasks = []
        for channel in self.channels.values():
            tasks.append(asyncio.ensure_future(
                channel.listen_produce(
                    self.on_channel_sent
                )))
        return tasks
