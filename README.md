# Stardust (WIP)

An actor framework capable of utilizing all available cores.

This is an attempt (failed one) to use async/await syntax with actors.

It seems like implementing custom event loop cannot be avoided.

Roadmap:
1. Make ActorSystem, LoadBalancer and inter-node communication algorithms actors. (in progress)
2. Implement custom asynchronous io on top of `selectors` module.
3. Bring LoadBalancer from one of old implementations (it works well and is dead-simple).
