from typing import Dict

from stardust.actor import ActorRef
from stardust.system.load_balancer.load_balancer_interface import AbstractLoadBalancer
from stardust.system.types import CoreID


class DefaultLoadBalancer(AbstractLoadBalancer):
    def __init__(self, actor_to_core, workers_count: int, difference_threshold: float = 0.2):
        self.core_to_actors = {core_id: [] for core_id in range(1, workers_count + 1)}
        self.actor_to_core = actor_to_core
        self.difference_threshold = difference_threshold
        self.workers_count = workers_count
        self.actor_class_to_core = dict()
        self.actor_to_actor_class = dict()

    def place(self, actor_class) -> CoreID:
        if actor_class not in self.actor_class_to_core:
            self.actor_class_to_core[actor_class] = {
                core_id: 0
                for core_id in range(1, self.workers_count + 1)
            }

        least_loaded_core = sorted(self.actor_class_to_core[actor_class].items(), key=lambda p: p[1])[0]
        least_loaded_core = least_loaded_core[0]

        return CoreID(least_loaded_core)

    def placed(self, actor_type, actor_ref: ActorRef, core_id: CoreID):
        self.actor_class_to_core[actor_type][core_id] += 1
        self.core_to_actors[core_id].append(actor_ref)
        self.actor_to_core[actor_ref] = core_id
        self.actor_to_actor_class[actor_ref] = actor_type

    def rebalance(self) -> Dict[ActorRef, CoreID]:
        return {}

    def kill(self, actor_ref: ActorRef):
        pass

    def removed(self, actor_ref: ActorRef):
        core = self.actor_to_core.pop(actor_ref)
        self.core_to_actors[core].remove(actor_ref)
        self.actor_class_to_core[self.actor_to_actor_class[actor_ref]] -= 1
        self.actor_to_actor_class.pop(actor_ref)
