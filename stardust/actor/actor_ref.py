class ActorRef:
    def __init__(self, node_id, actor_id):
        self.node_id = node_id
        self.actor_id = actor_id

    def __str__(self):
        return f"ActorRef<{self.node_id}.{self.actor_id}>"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, ActorRef):
            return False
        return self.node_id == other.node_id and self.actor_id == other.actor_id

    def __hash__(self):
        return hash(str(self))
