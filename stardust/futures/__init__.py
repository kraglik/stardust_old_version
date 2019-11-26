import asyncio
from typing import Optional


class InternalFuture(asyncio.Future):
    pass


class nice(InternalFuture):
    pass


class send(InternalFuture):
    def __init__(self, message, target):
        super().__init__()
        self.message = message
        self.target = target


class respond(InternalFuture):
    def __init__(self, message):
        super().__init__()
        self.message = message


class ask(InternalFuture):
    def __init__(self, message, target, timeout: Optional[float] = None):
        super().__init__()
        self.message = message
        self.target = target
        self.timeout = timeout


class spawn(InternalFuture):
    def __init__(self, actor_class, *args, **kwargs):
        super().__init__()
        self.actor_class = actor_class
        self.args = args
        self.kwargs = kwargs


class kill(InternalFuture):
    def __init__(self, target):
        super().__init__()
        self.target = target


class ref(InternalFuture):
    pass


class get_event_loop(InternalFuture):
    pass
