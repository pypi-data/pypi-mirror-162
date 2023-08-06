import abc
from typing import Generator

from edgechaos.executor.api import ChaosCommand


class ChaosCommandListener(abc.ABC):

    def listen(self) -> Generator[ChaosCommand, None, None]: ...

    def stop(self): ...

    @staticmethod
    def from_env(): ...
