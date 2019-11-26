from stardust.actor import Actor, ActorRef
from stardust.system import ActorSystem, Config
from stardust.futures import send, ask, nice, spawn, kill, respond, ref, get_event_loop
from stardust.messages import StartupMessage


class Pong(Actor):
    async def receive(self, message, sender):
        if message == 'ping':
            print(message)
            await respond('pong')


class Ping(Actor):
    async def receive(self, message, sender):
        if isinstance(message, StartupMessage):
            pong = await spawn(Pong)
            response = await ask('ping', pong)
            await kill(pong)
            print(response)

        elif message == 'stop':
            await respond('ok')


def main():
    config = Config(workers_count=12)
    system = ActorSystem(config)
    system.start()

    pings = []

    for i in range(100):
        ping = system.spawn(Ping)
        pings.append(ping)

    for ping in pings:
        system.ask('stop', ping)
        system.kill(ping)

    system.stop()


if __name__ == '__main__':
    main()
