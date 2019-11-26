import asyncio
from typing import Optional

from stardust.events import *


class InternalFuture(asyncio.Future):
    pass


class UserLevelFuture(InternalFuture):
    pass


class SystemLevelFuture(InternalFuture):
    def __init__(self, event: SystemLevelEvent):
        super().__init__()
        self.event = event


class nice(UserLevelFuture):
    pass


class send(UserLevelFuture):
    def __init__(self, message, target):
        super().__init__()
        self.message = message
        self.target = target


class respond(UserLevelFuture):
    def __init__(self, message):
        super().__init__()
        self.message = message


class ask(UserLevelFuture):
    def __init__(self, message, target, timeout: Optional[float] = None):
        super().__init__()
        self.message = message
        self.target = target
        self.timeout = timeout


class spawn(UserLevelFuture):
    def __init__(self, actor_class, *args, **kwargs):
        super().__init__()
        self.actor_class = actor_class
        self.args = args
        self.kwargs = kwargs


class kill(UserLevelFuture):
    def __init__(self, target):
        super().__init__()
        self.target = target

