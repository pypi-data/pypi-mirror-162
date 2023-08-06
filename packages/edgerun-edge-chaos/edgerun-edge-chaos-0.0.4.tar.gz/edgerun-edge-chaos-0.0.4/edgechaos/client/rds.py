import logging

import redis

from edgechaos.client.api import ChaosClient
from edgechaos.executor.api import ChaosCommand
from edgechaos.util.rds import redis_from_env

logger = logging.getLogger(__name__)


class RedisChaosClient(ChaosClient):

    def __init__(self, rds: redis.Redis):
        self.rds = rds

    def send(self, host: str, cmd: ChaosCommand):
        msg = ChaosCommand.to_json(cmd)
        channel = 'edgechaos/%s' % host
        logger.info(f'Client publishes on {channel}, command: {msg}')
        self.rds.publish(channel, msg)

    def stop(self):
        logger.info('Stop RedisChaosClient')
        self.rds.close()

    @staticmethod
    def from_env():
        return RedisChaosClient(redis_from_env())
