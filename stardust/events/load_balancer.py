class LoadBalancerEvent:
    pass


class BalanceSpawnEvent(LoadBalancerEvent):
    def __init__(
            self,
            spawn_request_event,
            actor_ref
    ):
        self.spawn_request_event = spawn_request_event
        self.actor_ref = actor_ref


class BalanceKillEvent(LoadBalancerEvent):
    def __init__(
            self,
            kill_response_event
    ):
        self.kill_response_event = kill_response_event


class BalancerUpdateSpawnedEvent(LoadBalancerEvent):
    def __init__(
            self,
            actor_class,
            spawn_response_event
    ):
        self.actor_class = actor_class
        self.spawn_response_event = spawn_response_event
