from stardust.actor.locality import Locality


class Actor:

    LOCALITY = Locality.NODE

    async def receive(self, message, sender):
        raise NotImplementedError("Actor must implement 'receive' method.")
