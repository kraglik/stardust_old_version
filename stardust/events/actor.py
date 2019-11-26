from stardust.actor.actor_ref import ActorRef


class ActorEvent:
    pass


class YieldControlEvent(ActorEvent):
    pass


class SendEvent(ActorEvent):
    def __init__(
            self,
            sender: ActorRef,
            message,
            target: ActorRef,
            context_code=None
    ):
        self.sender = sender
        self.target = target
        self.message = message
        self.context_code = context_code


class AskEvent(ActorEvent):
    def __init__(
            self,
            sender: ActorRef,
            message,
            target: ActorRef,
            context_code
    ):
        self.sender = sender
        self.target = target
        self.message = message
        self.context_code = context_code


class IncomingMessageEvent(ActorEvent):
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
        return f"IncomingMessage<from={self.sender}, to={self.target}, content={self.message}, context_code={self.context_code}>"


class SpawnRequestEvent(ActorEvent):
    def __init__(
            self,
            parent: ActorRef,
            actor_class,
            args,
            kwargs,
            context_code
    ):
        self.parent = parent
        self.actor_class = actor_class
        self.args = args
        self.kwargs = kwargs
        self.context_code = context_code


class KillRequestEvent(ActorEvent):
    def __init__(
            self,
            sender: ActorRef,
            target: ActorRef
    ):
        self.sender = sender
        self.target = target
