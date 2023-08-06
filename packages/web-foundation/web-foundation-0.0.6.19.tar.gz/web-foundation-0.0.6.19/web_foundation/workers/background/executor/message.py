from functools import partial
from typing import Callable, Any, Coroutine, TypeVar, Generic

from web_foundation.kernel import IMessage

BgTask = TypeVar("BgTask", Callable[..., Coroutine[Any, Any, Any]], partial)


class TaskIMessage(Generic[BgTask], IMessage):
    message_type = "background_task"
    task: BgTask
    args: Any | None
    kwargs: Any | None

    def __init__(self, task: BgTask, args: Any = None, kwargs: Any | None = None):
        super().__init__()
        self.task = task
        self.args = args
        self.kwargs = kwargs
