import abc

from edgechaos.executor.api import ChaosCommand


class ChaosClient(abc.ABC):

    def send(self, host: str, cmd: ChaosCommand): ...

    @staticmethod
    def from_env(): ...
