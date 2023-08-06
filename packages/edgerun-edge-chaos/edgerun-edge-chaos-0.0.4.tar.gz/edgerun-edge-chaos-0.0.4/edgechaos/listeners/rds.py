import json
import logging
from typing import Generator, Dict

import redis

from edgechaos.executor.api import ChaosCommand
from edgechaos.listeners.api import ChaosCommandListener
from edgechaos.util.rds import redis_from_env, read_channel

logger = logging.getLogger(__name__)

POISON_PILL = 'STOP'


class RedisChaosCommandListener(ChaosCommandListener):

    def __init__(self, channel: str, rds: redis.Redis):
        self.rds = rds
        self.channel = channel
        self.running = True

    def listen(self) -> Generator[ChaosCommand, None, None]:
        sub = self.rds.pubsub()
        sub.subscribe(self.channel)
        try:
            for msg in sub.listen():
                logger.debug(f'Got message: {msg}')
                if msg is None:
                    continue
                if msg['data'] == POISON_PILL:
                    self.running = False
                    break
                data = msg['data']
                try:
                    if isinstance(data, Dict):
                        dump = json.dumps(data)
                        yield ChaosCommand.from_json(dump)
                    elif isinstance(data, str):
                        yield ChaosCommand.from_json(data)
                except Exception as e:
                    logger.error('Reading command failed', e)
        except Exception as e:
            logger.error(e)
        finally:
            sub.close()
            logger.info("Stopping RedisChaosCommandListener...")

    def stop(self):
        if self.running:
            self.running = False
            self.rds.publish(self.channel, POISON_PILL)

    @staticmethod
    def from_env() -> 'RedisChaosCommandListener':
        channel = read_channel()
        logger.info(f'RedisChaosCommandListener listens on {channel}')
        return RedisChaosCommandListener(channel, redis_from_env())
