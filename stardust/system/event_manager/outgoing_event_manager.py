from threading import Thread
from queue import Queue

from stardust.events import *


class OutgoingEventManager(Thread):

    def __init__(self, system, outgoing_queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system = system
        self.outgoing_queue = outgoing_queue

    def run(self) -> None:
        while True:
            event = self.outgoing_queue.get()

            if isinstance(event, StopExecution):
                break

            else:
                self.process_event(event)

        self.stop_workers()

    def process_event(self, event):
        if isinstance(event, SpawnEvent):
            self.spawn(event)
        elif isinstance(event, KillEvent):
            self.kill(event)
        elif isinstance(event, SpawnResponseEvent):
            self.notify_spawned(event)
        elif isinstance(event, ActorPlacementDiffEvent):
            self.notify_diff(event)
        elif isinstance(event, MessageEvent):
            self.send_message(event)

    def spawn(self, event: SpawnEvent):
        self.system.queues[event.core_id].put(event)

    def kill(self, event: KillEvent):
        core = self.system.load_balancer.algo.actor_to_core[event.target]
        self.system.queues[core].put(event)

    def notify_diff(self, event):
        for core_id, queue in self.system.queues.items():
            if core_id != 0:
                queue.put(event)

    def notify_spawned(self, event: SpawnResponseEvent):
        core_id = self.system.actor_to_core[event.parent]
        self.system.queues[core_id].put(event)

    def send_message(self, event: MessageEvent):
        core = self.system.actor_to_core[event.target]
        self.system.queues[core].put(event)

    def stop_workers(self):
        for core_id, queue in self.system.queues.items():
            if core_id != 0:
                queue.put(StopExecution())
