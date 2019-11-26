from uuid import uuid4
from collections import deque

from stardust.actor.actor import Actor
from stardust.actor.actor_ref import ActorRef
from stardust.futures import *
from stardust.events import *


DONE = 'DONE'


class Cell:
    def __init__(
            self,
            actor: Actor,
            ref: ActorRef,
            parent_ref: ActorRef,
            mailbox: deque
    ):
        self.ref = ref
        self.parent_ref = parent_ref
        self.actor = actor
        self.mailbox = mailbox or deque()
        self.behaviours = []
        self._current_behaviour = self.actor.receive
        self.executing_generator = None
        self.awaited_context = None
        self.awaited_response = None
        self.poisoned = False
        self.last_event = None

    def push(self, message):
        self.mailbox.append(message)

    def push_left(self, message):
        self.mailbox.appendleft(message)

    def pop(self):
        return self.mailbox.popleft()

    def process(self, worker):
        event = self.pop()
        if isinstance(event, IncomingMessageEvent):
            context_code = event.context_code
        else:
            context_code = None

        coroutine = self._current_behaviour(event.message, event.sender)

        try:
            resp = coroutine.send(None)

            while True:
                if isinstance(resp, send):
                    yield SendEvent(
                        sender=self.ref,
                        target=resp.target,
                        message=resp.message
                    )
                    resp.set_result(None)
                    resp = coroutine.send(None)

                elif isinstance(resp, ask):
                    response = yield AskEvent(
                        sender=self.ref,
                        target=resp.target,
                        message=resp.message,
                        context_code=uuid4().int
                    )
                    resp.set_result(response)
                    resp = coroutine.send(None)

                elif isinstance(resp, respond):
                    yield SendEvent(
                        sender=self.ref,
                        target=event.sender,
                        message=resp.message,
                        context_code=context_code
                    )
                    resp.set_result(None)
                    resp = coroutine.send(None)

                elif isinstance(resp, spawn):
                    response = yield SpawnRequestEvent(
                        parent=self.ref,
                        actor_class=resp.actor_class,
                        args=resp.args,
                        kwargs=resp.kwargs,
                        context_code=uuid4().int
                    )
                    resp.set_result(response)
                    resp = coroutine.send(None)

                elif isinstance(resp, kill):
                    response = yield KillRequestEvent(
                        sender=self.ref,
                        target=resp.target
                    )
                    resp.set_result(None)
                    resp = coroutine.send(None)

        except StopIteration:
            yield DONE

    def __str__(self):
        return f"Cell<actor_type={type(self.actor)}, ref={self.ref}>"

    def __repr__(self):
        return str(self)
