from typing import Optional
from uuid import uuid4
from multiprocessing import Queue as MPQueue
from queue import Queue

from stardust.actor.actor_ref import ActorRef
from stardust.events import *
from stardust.messages import PoisonPillMessage
from stardust.system.config import Config
from stardust.system.types import CoreID, NodeID, ActorID
from stardust.system.worker import Worker
from stardust.system.load_balancer import DefaultLoadBalancer, LoadBalancer
from stardust.system.event_manager import IncomingEventManager, OutgoingEventManager


class ActorSystem:

    def __init__(self, config: Config):
        self.config = config
        self.ref = ActorRef(node_id=NodeID(uuid4().int), actor_id=ActorID(0))
        self.queues = self._create_queues()
        self.workers = self._create_workers()

        self.actor_to_core = dict()
        self.load_balancer = LoadBalancer(
            load_balancing_algo=DefaultLoadBalancer(
                actor_to_core=self.actor_to_core,
                workers_count=self.config.workers_count
            ),
            system=self
        )
        self.outgoing_queue = Queue()
        self.communication_queue = Queue()

        self.incoming_event_manager = IncomingEventManager(
            input_queue=self.queues[0],
            system=self
        )
        self.outgoing_event_manager = OutgoingEventManager(
            outgoing_queue=self.outgoing_queue,
            system=self
        )
        self.awaited_context = None

    def _create_queues(self):
        return {
            CoreID(core): MPQueue()
            for core in range(self.config.workers_count + 1)
        }

    def _create_workers(self):
        return [
            Worker(
                CoreID(core),
                self.queues,
                self.ref
            )
            for core in range(1, self.config.workers_count + 1)
        ]

    def start(self):
        self.incoming_event_manager.start()
        self.outgoing_event_manager.start()
        self.load_balancer.start()

        for worker in self.workers:
            worker.start()

    def spawn(self, actor_type, *args, **kwargs) -> ActorRef:
        context_code = uuid4().int
        self.queues[0].put(
            SpawnRequestEvent(
                parent=self.ref,
                actor_class=actor_type,
                args=args,
                kwargs=kwargs,
                context_code=context_code
            )
        )
        ref = self.communication_queue.get()
        return ref

    def kill(self, actor_ref):
        self.awaited_context = actor_ref
        self.outgoing_queue.put(
            KillEvent(
                sender=self.ref,
                target=actor_ref,
                message=PoisonPillMessage()
            )
        )
        self.communication_queue.get()

    def send(self, message, target: ActorRef):
        self.outgoing_queue.put(
            MessageEvent(
                sender=self.ref,
                message=message,
                target=target,
                context_code=None
            )
        )

    def ask(self, message, target: ActorRef):
        self.awaited_context = uuid4().int
        self.outgoing_queue.put(
            MessageEvent(
                sender=self.ref,
                message=message,
                target=target,
                context_code=self.awaited_context
            )
        )
        response = self.communication_queue.get()
        return response

    def stop(self):
        self.queues[0].put(StopExecution())

        for worker in self.workers:
            worker.join()

        self.load_balancer.join()
        self.incoming_event_manager.join()
        self.outgoing_event_manager.join()
