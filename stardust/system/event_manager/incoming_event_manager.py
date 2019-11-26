from uuid import uuid4
from threading import Thread
from queue import Queue

from stardust.actor import ActorRef
from stardust.events import *
from stardust.system.types import ActorID


class IncomingEventManager(Thread):

    def __init__(self, system, input_queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system = system
        self.input_queue = input_queue
        self.pending_spawn_requests = dict()

    def run(self) -> None:
        while True:
            event = self.input_queue.get()

            if isinstance(event, StopExecution):
                break

            else:
                self.process_event(event)

        self.system.load_balancer.queue.put(StopExecution())
        self.system.outgoing_queue.put(StopExecution())

    def process_event(self, event):
        if isinstance(event, SpawnRequestEvent):
            self.spawn(event)
        elif isinstance(event, KillRequestEvent):
            self.kill(event)
        elif isinstance(event, SpawnResponseEvent):
            self.notify_spawned(event)
        elif isinstance(event, KillResponseEvent):
            self.notify_killed(event)
        elif isinstance(event, MessageEvent):
            self.receive_message(event)

    def spawn(self, event: SpawnRequestEvent):
        ref = ActorRef(node_id=self.system.ref.node_id, actor_id=ActorID(uuid4().int))
        lb_event = BalanceSpawnEvent(event, ref)
        self.pending_spawn_requests[ref] = event.actor_class
        self.system.load_balancer.queue.put(lb_event)

    def kill(self, event: KillRequestEvent):
        self.system.load_balancer.queue.put(event)

    def notify_spawned(self, event: SpawnResponseEvent):
        lb_event = BalancerUpdateSpawnedEvent(
            self.pending_spawn_requests.pop(event.child),
            event
        )
        self.system.load_balancer.queue.put(lb_event)

    def notify_killed(self, event: KillResponseEvent):
        lb_event = BalanceKillEvent(
            event
        )
        self.system.load_balancer.queue.put(lb_event)

    def receive_message(self, event: MessageEvent):
        if event.target == self.system.ref and self.system.awaited_context == event.context_code:
            self.system.communication_queue.put(event.message)
