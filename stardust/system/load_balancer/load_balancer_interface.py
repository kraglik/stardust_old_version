from abc import ABC, abstractmethod
from typing import Dict

from stardust.system.types import CoreID, ActorID
from stardust.actor import ActorRef


class AbstractLoadBalancer(ABC):

    @abstractmethod
    def place(self, actor_class) -> CoreID:
        """
        This method is required to determine first worker to host new actor of given type.
        :param actor_class:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def placed(self, actor_type, actor_ref: ActorRef, core_id: CoreID):
        """
        This method is called by the system after successful actor placement.
        It also makes newly spawned actor visible for a load balancing mechanism.
        :param actor_type:
        :param actor_ref:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def kill(self, actor_ref: ActorRef):
        """

        :param actor_ref:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def removed(self, actor_ref: ActorRef):
        """

        :param actor_ref:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def rebalance(self) -> Dict[ActorRef, CoreID]:
        """

        :return:
        """
        raise NotImplementedError
