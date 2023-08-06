import os
from typing import Optional

from edgechaos.client.api import ChaosClient
from edgechaos.client.rds import RedisChaosClient
from edgechaos.client.rmq import RabbitMqChaosClient


def create_client() -> Optional[ChaosClient]:
    client_type = os.environ.get('edgechaos_client_type')
    if client_type == 'redis':
        return RedisChaosClient.from_env()
    elif client_type == 'rabbitmq':
        return RabbitMqChaosClient.from_env()
    else:
        raise ValueError(f'Unknown client type received `{client_type}`')
