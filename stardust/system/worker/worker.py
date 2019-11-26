import asyncio

from multiprocessing import Process, Queue as MPQueue
from typing import Dict
from queue import Queue
from collections import deque
from threading import Condition, Thread

from stardust.actor import ActorRef, Cell
from stardust.actor.cell import DONE, NICE
from stardust.events import *
from stardust.futures import InternalFuture
from stardust.system.types import CoreID
from stardust.system.worker.incoming_event_manager import IncomingEventManager
from stardust.system.worker.outgoing_event_manager import OutgoingEventManager


def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


class Worker(Process):
    def __init__(
            self,
            id: CoreID,
            queue_map: Dict[CoreID, MPQueue],
            system_ref: ActorRef,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.id = id
        self.queue_map = queue_map
        self.output_queue = Queue()
        self.system_ref = system_ref
        self.event_loop = None
        self.asyncio_thread = None
        self.actor_to_core = dict()

        self.all_actors: Dict[ActorRef, Cell] = dict()
        self.active_actors: deque[Cell] = deque()
        self.inactive_actors: Dict[ActorRef, Cell] = dict()

        self.exec_condition = Condition()
        self.is_running: bool = True

        self.incoming_event_manager = IncomingEventManager(self)
        self.outgoing_event_manager = OutgoingEventManager(self)

    def run(self) -> None:
        self.event_loop = asyncio.new_event_loop()
        self.asyncio_thread = Thread(target=start_background_loop, args=(self.event_loop,), daemon=True)
        self.asyncio_thread.start()
        self.incoming_event_manager.start()
        self.outgoing_event_manager.start()

        while self.is_running:
            with self.exec_condition:
                while len(self.active_actors) == 0 and self.is_running:
                    self.exec_condition.wait()

            if not self.is_running:
                break

            cell = self.active_actors.popleft()

            self.process_cell(cell)

        self.shutdown()

    def shutdown(self):
        self.output_queue.put(StopExecution())

        self.incoming_event_manager.join()
        self.outgoing_event_manager.join()

        self.queue_map[CoreID(0)].put(WorkerStopped())

    def put_message_event(self, event: MessageEvent):
        cell = self.all_actors[event.target]
        if event.context_code == cell.awaited_context and cell.awaited_context is not None:
            cell.awaited_response = event.message
        else:
            incoming_message = IncomingMessageEvent(
                event.sender,
                event.target,
                event.message,
                event.context_code
            )
            cell.push(incoming_message)

        if cell.ref in self.inactive_actors:
            if cell.awaited_context == event.context_code or cell.awaited_context is None:
                self.inactive_actors.pop(cell.ref)
                self.active_actors.append(cell)

                with self.exec_condition:
                    self.exec_condition.notify_all()

    def process_cell(self, cell):
        gen = cell.executing_generator or cell.process(self)
        cell.executing_generator = None

        event = cell.awaited_response
        cell.awaited_response = None
        cell.awaited_context = None
        event = gen.send(event)

        while True:
            if event is None:
                event = gen.send(None)

            elif isinstance(event, SpawnRequestEvent):
                cell.executing_generator = gen
                cell.awaited_context = event.context_code
                self.output_queue.put(event)
                self.inactive_actors[cell.ref] = cell
                break

            elif isinstance(event, SendEvent):
                self.output_queue.put(
                    MessageEvent(
                        sender=event.sender,
                        target=event.target,
                        message=event.message,
                        context_code=event.context_code
                    )
                )
                event = gen.send(None)

            elif isinstance(event, AskEvent):
                cell.executing_generator = gen
                cell.awaited_context = event.context_code
                self.output_queue.put(
                    MessageEvent(
                        sender=event.sender,
                        target=event.target,
                        message=event.message,
                        context_code=event.context_code
                    )
                )
                self.inactive_actors[cell.ref] = cell
                break

            elif isinstance(event, KillRequestEvent):
                self.output_queue.put(event)
                event = gen.send(None)

            elif event == NICE:
                self.active_actors.append(cell)
                break

            elif event == DONE:
                if len(cell.mailbox) == 0:
                    self.inactive_actors[cell.ref] = cell
                else:
                    self.active_actors.append(cell)
                break
