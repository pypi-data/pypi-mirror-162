import logging
import os
import time

from edgechaos.client.factory import create_client
from edgechaos.executor.api import ChaosCommand

logging.basicConfig(level=os.environ.get('edgechaos_logging_level', 'INFO'))
logger = logging.getLogger(__name__)


def main():
    client = None
    try:
        logger.info('Start client')
        client = create_client()
        if client is None:
            logger.error('Client is None')
            return

        target_host = 'freyr'
        interface = 'lo'

        test_tc_add_remove_latency(client, target_host, interface)
    finally:
        if client is not None:
            client.stop()

def test_tc_add_remove_latency(client, target_host, interface):
    start_tc_params = [
        "qdisc",
        "add",
        "dev",
        interface,
        "root",
        "netem",
        "delay",
        "100ms"
    ]

    stop_tc_params = [
        "qdisc",
        "del",
        "dev",
        interface,
        "root",
        "netem",
        "delay",
        "100ms"
    ]

    start_cmd = ChaosCommand('tc', {'tc': start_tc_params}, 'start')
    stop_cmd = ChaosCommand('tc', {'tc': stop_tc_params}, 'stop')

    client.send(target_host, start_cmd)
    time.sleep(10)
    client.send(target_host, stop_cmd)


def test_stress_ng_cpu(client, target_host):
    cmd = ChaosCommand('stress-ng', {'cpu': 8}, 'start')
    client.send(target_host, cmd)
    time.sleep(5)
    cmd = ChaosCommand('stress-ng', {'cpu': 8}, 'stop')
    client.send(target_host, cmd)


if __name__ == '__main__':
    main()
