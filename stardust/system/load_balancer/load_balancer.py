from threading import Thread
from queue import Queue

from stardust.events import *
from stardust.messages import PoisonPillMessage
from stardust.system.load_balancer.load_balancer_interface import AbstractLoadBalancer


class LoadBalancer(Thread):
    def __init__(self, load_balancing_algo: AbstractLoadBalancer, system, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.algo = load_balancing_algo
        self.system = system
        self.queue = Queue()

    def run(self) -> None:
        while True:
            event = self.queue.get()

            if isinstance(event, StopExecution):
                break

            else:
                self.process_event(event)

    def process_event(self, event):
        if isinstance(event, BalanceSpawnEvent):
            self.place_actor(event)
        elif isinstance(event, KillRequestEvent):
            self.schedule_actor_removal(event)
        elif isinstance(event, BalanceKillEvent):
            self.remove_actor(event)
        elif isinstance(event, BalancerUpdateSpawnedEvent):
            self.placed_actor(event)

    def place_actor(self, event: BalanceSpawnEvent):
        target_core = self.algo.place(event.spawn_request_event.actor_class)
        self.system.outgoing_queue.put(
            SpawnEvent(
                core_id=target_core,
                actor_class=event.spawn_request_event.actor_class,
                args=event.spawn_request_event.args,
                kwargs=event.spawn_request_event.kwargs,
                ref=event.actor_ref,
                parent=event.spawn_request_event.parent,
                context_code=event.spawn_request_event.context_code
            )
        )

    def schedule_actor_removal(self, event):
        self.system.outgoing_queue.put(
            KillEvent(
                message=PoisonPillMessage(),
                sender=event.sender,
                target=event.target
            )
        )

    def remove_actor(self, event: BalanceKillEvent):
        self.system.actor_to_core.pop(event.kill_response_event.target)

        if self.system.awaited_context == event.kill_response_event.target:
            self.system.communication_queue.put(event.kill_response_event.target)

    def placed_actor(self, event: BalancerUpdateSpawnedEvent):
        if not event.spawn_response_event.error:
            self.algo.placed(
                event.actor_class,
                event.spawn_response_event.child,
                event.spawn_response_event.core_id
            )

        self.system.outgoing_queue.put(
            ActorPlacementDiffEvent(
                diff={
                    event.spawn_response_event.child: event.spawn_response_event.core_id
                }
            )
        )

        if event.spawn_response_event.parent == self.system.ref:
            self.system.communication_queue.put(event.spawn_response_event.child)
        else:
            self.system.outgoing_queue.put(event.spawn_response_event)

