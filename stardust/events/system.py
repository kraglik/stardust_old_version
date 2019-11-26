from typing import Optional, Dict

from stardust.actor.actor_ref import ActorRef
from stardust.messages import StartupMessage


class SystemLevelEvent:
    pass


class MessageEvent(SystemLevelEvent):
    def __init__(
            self,
            sender: ActorRef,
            target: ActorRef,
            message,
            context_code
    ):
        self.sender = sender
        self.target = target
        self.message = message
        self.context_code = context_code

    def __str__(self):
        return f"Message<from={self.sender}, to={self.target}, content={self.message}, context_code={self.context_code}>"


class StartupEvent(SystemLevelEvent):
    def __init__(
            self,
            sender: ActorRef,
            target: ActorRef
    ):
        self.sender = sender
        self.target = target
        self.message = StartupMessage()


class SpawnEvent(SystemLevelEvent):
    def __init__(
            self,
            parent: ActorRef,
            ref: ActorRef,
            actor_class,
            core_id,
            context_code,
            args,
            kwargs
    ):
        self.parent = parent
        self.ref = ref
        self.actor_class = actor_class
        self.core_id = core_id
        self.args = args
        self.kwargs = kwargs
        self.context_id = context_code


class KillEvent(SystemLevelEvent):
    def __init__(
            self,
            sender: ActorRef,
            target: ActorRef,
            message
    ):
        self.sender = sender
        self.target = target
        self.message = message


class SpawnResponseEvent(SystemLevelEvent):
    def __init__(
            self,
            parent: ActorRef,
            child: Optional[ActorRef],
            error: Optional[Exception],
            core_id,
            context_code,
            target_core_id=None
    ):
        self.parent = parent
        self.child = child
        self.error = error
        self.core_id = core_id
        self.target_core_id = target_core_id
        self.context_code = context_code


class KillResponseEvent(SystemLevelEvent):
    def __init__(
            self,
            sender: ActorRef,
            target: ActorRef,
            success: bool
    ):
        self.sender = sender
        self.target = target
        self.success = success


class ActorPlacementDiffEvent(SystemLevelEvent):
    def __init__(
            self,
            diff: Dict[ActorRef, int]
    ):
        self.diff = diff


class StopExecution(SystemLevelEvent):
    pass


class WorkerStopped(SystemLevelEvent):
    pass
