from typing import Generic, Type

from web_foundation.kernel import IMessage
from web_foundation.workers.background.executor.message import BgTask, TaskIMessage
from web_foundation.workers.worker import GenWorker


class Service(Generic[GenWorker]):
    _worker: GenWorker

    async def run_background(self, task: BgTask, *args, **kwargs):
        await self._worker.channel.produce(
            TaskIMessage(task, args=args, kwargs=kwargs)
        )

    @property
    def worker(self) -> GenWorker:
        return self._worker

    @worker.setter
    def worker(self, worker: GenWorker):
        self._worker = worker

    async def emmit_event(self, event: IMessage):
        await self._worker.channel.produce(event)
