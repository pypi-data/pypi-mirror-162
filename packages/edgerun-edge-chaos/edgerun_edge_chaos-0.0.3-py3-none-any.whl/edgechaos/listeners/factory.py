import os
from typing import Optional

from edgechaos.listeners.api import ChaosCommandListener
from edgechaos.listeners.rds import RedisChaosCommandListener


def create_listener() -> Optional[ChaosCommandListener]:
    listener_type = os.environ.get('edgechaos_listener_type')
    if listener_type == 'redis':
        return RedisChaosCommandListener.from_env()
    else:
        return None
