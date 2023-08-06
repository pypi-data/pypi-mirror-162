import logging
import os

import redis

logger = logging.getLogger(__name__)


def redis_from_env():
    host = os.environ.get('edgechaos_redis_host', 'localhost')
    params = {
        'host': host,
        'port': int(os.environ.get('edgechaos_redis_port', '6379')),
        'decode_responses': True,
        'charset': 'utf-8',
    }

    if os.environ.get('edgechaos_redis_password') is not None:
        params['password'] = os.environ.get('edgechaos_redis_password')

    logger.debug('establishing redis connection with params %s', params)

    return redis.Redis(**params)


def read_channel():
    edgechaos_host = os.environ.get('edgechaos_host')

    if edgechaos_host is None:
        logger.info('edgechaos_host env variable not set, default to HOSTNAME')
        edgechaos_host = os.environ.get('HOSTNAME')

    return f'edgechaos/{edgechaos_host}'
