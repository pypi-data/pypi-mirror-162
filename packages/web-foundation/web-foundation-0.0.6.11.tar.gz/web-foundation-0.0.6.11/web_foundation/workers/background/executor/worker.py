import asyncio
import datetime
import uuid
from asyncio import Task
from dataclasses import dataclass, field
from functools import partial
from typing import Dict, Any
from time import time_ns
from dependency_injector import containers
from loguru import logger
from inspect import iscoroutine
from web_foundation.workers.background.executor.message import TaskIMessage
from web_foundation.workers.worker import Worker


@dataclass
class BackgroundTask:
    task: Task[Any]
    status: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    exec_time: int = field(default=0)
    done_time: int = field(default=0)
    call_time: float = field(default=0)
    finish_time: datetime.datetime | None = field(default_factory=datetime.datetime.now)
    start_time: datetime.datetime | None = field(default_factory=datetime.datetime.now)
    error: BaseException | None = field(default=None)


class TaskExecutor(Worker):
    _runned_task: Dict[uuid.UUID, BackgroundTask]
    _completed_tasks: Dict[uuid.UUID, BackgroundTask]
    _errors_task: Dict[uuid.UUID, BackgroundTask]

    def wire_worker(self, container: containers.DeclarativeContainer) -> None:
        pass

    def __init__(self, **kwargs):
        self._runned_task = {}
        self._completed_tasks = {}
        self._errors_task = {}
        super().__init__(**kwargs)

    async def _run(self):
        self.channel.add_event_listener(TaskIMessage, self.task_handler)
        await self.channel.listen_consume()

    async def task_handler(self, message: TaskIMessage):
        task = asyncio.create_task(message.task(*message.args, **message.kwargs))  # type: ignore
        arc_task = BackgroundTask(task=task, status="pending")
        arc_task.exec_time = time_ns()
        self._runned_task[arc_task.id] = arc_task
        # TODO Think about responses
        task.add_done_callback(partial(self.on_task_done, arc_task=arc_task))

    def on_task_done(self, task: Task, arc_task: BackgroundTask):
        arc_task.done_time = time_ns()
        arc_task.call_time = (arc_task.done_time - arc_task.exec_time) / 1000000000
        exeption = task.exception()
        if exeption:
            self._errors_task[arc_task.id] = self._runned_task.pop(arc_task.id)
            arc_task.status = f"error {exeption.__str__()}"
            arc_task.error = exeption
            if self.debug:
                logger.warning(f"Task {arc_task.id} provide error {exeption.__str__()} in {arc_task.call_time}")
        else:
            self._completed_tasks[arc_task.id] = self._runned_task.pop(arc_task.id)
            if self.debug:
                logger.info(f"Task {arc_task.id} done in {arc_task.call_time}")
            arc_task.status = "success"

    def _close(self, *args, **kwargs):
        pass

    def get_task_stats(self):
        result = {}
        for dictionary in [self._runned_task, self._errors_task, self._completed_tasks]:
            result.update(dictionary)
        return result
