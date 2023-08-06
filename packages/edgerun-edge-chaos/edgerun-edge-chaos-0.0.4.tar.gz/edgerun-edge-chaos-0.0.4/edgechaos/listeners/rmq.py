import logging
import os
from typing import Generator

import pika

from edgechaos.executor.api import ChaosCommand
from edgechaos.listeners.api import ChaosCommandListener
from edgechaos.util.env import read_host_env
from edgechaos.util.rmq import connection_from_env, try_setup_exchange, try_setup_queue

logger = logging.getLogger(__name__)

POISON_PILL = 'STOP'


class RabbitMqChaosCommandListener(ChaosCommandListener):

    def __init__(self, exchange: str, routing_key: str, queue_name: str, channel, connection: pika.BlockingConnection):
        self.exchange = exchange
        self.routing_key = routing_key
        self.queue_name = queue_name
        self.connection = connection
        self.channel = channel
        self.running = True

    def listen(self) -> Generator[ChaosCommand, None, None]:
        channel = None
        try:
            channel = self.channel

            for method_frame, properties, body in channel.consume(queue=self.queue_name, auto_ack=True):
                logger.debug(f'Got message: {body}')
                body = body.decode()
                if body == POISON_PILL:
                    self.running = False
                    break
                try:
                    yield ChaosCommand.from_json(body)
                except Exception as e:
                    logger.error('Reading command failed', e)
        except Exception as e:
            logger.error(f'Listening failed', e)
        finally:
            logger.info('Closing RabbitMqChaosCommandListener')
            if channel is not None:
                channel.close()
            self.connection.close()

    def stop(self):
        try:
            self.channel.basic_publish(self.exchange, self.routing_key, bytes(POISON_PILL))
        except Exception as e:
            logger.error(e)

    @staticmethod
    def from_env():
        logging.getLogger("pika").setLevel(logging.WARNING)
        connection = None
        channel = None
        try:
            connection = connection_from_env()
            channel = connection.channel()
            edgechaos_host = read_host_env()
            exchange = os.environ.get('edgechaos_rabbitmq_exchange', 'edgechaos')
            try_setup_exchange(channel, exchange)
            queue_name = try_setup_queue(channel, exchange, edgechaos_host)
            return RabbitMqChaosCommandListener(exchange, edgechaos_host, queue_name, channel, connection)
        except Exception as e:
            logger.error('Error during instantiating RabbitMqChaosCommandListener from env', e)
            channel.close()
            connection.close()