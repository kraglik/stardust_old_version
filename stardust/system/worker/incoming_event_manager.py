from collections import deque
from threading import Thread

from stardust.actor import Cell
from stardust.events import *


class IncomingEventManager(Thread):

    def __init__(self, worker, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.worker = worker

    def run(self) -> None:
        queue = self.worker.queue_map[self.worker.id]

        while True:
            event = queue.get()

            if isinstance(event, StopExecution):
                break

            self.process_event(event)

        self.worker.is_running = False
        with self.worker.exec_condition:
            self.worker.exec_condition.notify_all()

    def process_event(self, event):
        if isinstance(event, MessageEvent):
            self.put_message(event)
        elif isinstance(event, SpawnEvent):
            self.spawn_actor(event)
        elif isinstance(event, KillEvent):
            self.kill_actor(event)
        elif isinstance(event, SpawnResponseEvent):
            self.notify_spawned(event)
        elif isinstance(event, ActorPlacementDiffEvent):
            self.update_actor_locations(event)

    def put_message(self, event: MessageEvent):
        self.worker.put_message_event(event)

    def kill_actor(self, event: KillEvent):

        cell = self.worker.all_actors[event.target]

        if cell.executing_generator is None and cell.ref in self.worker.inactive_actors:

            self.worker.inactive_actors.pop(cell.ref)
            self.worker.all_actors.pop(cell.ref)
            self.worker.output_queue.put(
                KillResponseEvent(
                    sender=self.worker.system_ref,
                    target=event.target,
                    success=True
                )
            )

        else:
            cell.poisoned = True

    def spawn_actor(self, event: SpawnEvent):

        error = None

        try:
            actor_object = event.actor_class(*event.args, **event.kwargs)
            cell = Cell(
                parent_ref=event.parent,
                ref=event.ref,
                actor=actor_object,
                mailbox=deque()
            )
            self.worker.all_actors[cell.ref] = cell
            cell.push(StartupEvent(sender=self.worker.system_ref, target=cell.ref))
            self.worker.active_actors.append(cell)
            with self.worker.exec_condition:
                self.worker.exec_condition.notify_all()

        except Exception as e:
            error = e

        self.worker.output_queue.put(
            SpawnResponseEvent(
                child=event.ref,
                parent=event.parent,
                error=error,
                core_id=self.worker.id,
                context_code=event
            )
        )

    def notify_spawned(self, event):
        self.worker.actor_to_core[event.core_id] = event.child
        cell = self.worker.inactive_actors.pop(event.parent)
        cell.awaited_response = event.child
        self.worker.active_actors.append(cell)

        with self.worker.exec_condition:
            self.worker.exec_condition.notify_all()

    def update_actor_locations(self, event: ActorPlacementDiffEvent):
        self.worker.actor_to_core.update(event.diff)
