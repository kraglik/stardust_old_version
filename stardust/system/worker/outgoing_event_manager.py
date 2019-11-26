from threading import Thread

from stardust.events import *


class OutgoingEventManager(Thread):

    def __init__(self, worker, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.worker = worker

    def run(self) -> None:
        queue = self.worker.output_queue

        while True:
            event = queue.get()

            if isinstance(event, StopExecution):
                break

            self.process_event(event)

    def process_event(self, event):
        if isinstance(event, MessageEvent):
            self.send_message(event)
        elif isinstance(event, SpawnRequestEvent):
            self.request_spawn(event)
        elif isinstance(event, SpawnResponseEvent):
            self.response_spawn(event)
        elif isinstance(event, KillRequestEvent):
            self.request_spawn(event)
        elif isinstance(event, KillResponseEvent):
            self.response_spawn(event)

    def send_message(self, event: MessageEvent):
        if event.target == self.worker.system_ref:
            self.worker.queue_map[0].put(event)

        else:

            target_core = self.worker.actor_to_core[event.target]

            if target_core == self.worker.id:
                self.worker.put_message_event(event)
            else:
                self.worker.queue_map[target_core].put(event)

    def request_spawn(self, event):
        self.worker.queue_map[0].put(event)

    def response_spawn(self, event):
        self.worker.queue_map[0].put(event)

    def response_kill(self, event):
        self.worker.queue_map[0].put(event)
