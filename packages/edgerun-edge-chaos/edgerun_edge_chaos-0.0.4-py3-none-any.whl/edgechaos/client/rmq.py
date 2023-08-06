import logging
import os

import pika

from edgechaos.client.api import ChaosClient
from edgechaos.executor.api import ChaosCommand
from edgechaos.util.rmq import connection_from_env, try_setup_exchange

logger = logging.getLogger(__name__)


class RabbitMqChaosClient(ChaosClient):

    def __init__(self, exchange: str, channel, connection: pika.BlockingConnection):
        self.exchange = exchange
        self.channel = channel
        self.connection = connection

    def send(self, host: str, cmd: ChaosCommand):
        json_cmd = ChaosCommand.to_json(cmd)
        try:
            logger.info(f'Client sends command {json_cmd}')
            self.channel.basic_publish(self.exchange, host, json_cmd)
        except Exception as e:
            logger.error(f'Error happened sending command {json_cmd}', e)

    def stop(self):
        logger.info('Stop RabbitMqChaosClient')
        self.channel.close()
        self.connection.close()

    @staticmethod
    def from_env() -> 'RabbitMqChaosClient':
        logging.getLogger("pika").setLevel(logging.WARNING)
        connection = connection_from_env()
        channel = connection.channel()
        exchange = os.environ.get('edgechaos_rabbitmq_exchange', 'edgechaos')
        try_setup_exchange(channel, exchange)
        return RabbitMqChaosClient(exchange, channel, connection)
