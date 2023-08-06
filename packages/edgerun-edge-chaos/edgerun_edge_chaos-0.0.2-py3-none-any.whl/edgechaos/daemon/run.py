import logging
import os
import signal
from typing import Dict

from edgechaos.daemon.core import EdgeChaosDaemon
from edgechaos.executor.api import ChaosCommandExecutor
from edgechaos.executor.stressng import StressNgCommandExecutor
from edgechaos.listeners.factory import create_listener
from edgechaos.util.process import ProcessManager

logging.basicConfig(level=os.environ.get('edgechaos_logging_level', 'INFO'))
logger = logging.getLogger(__name__)


def sigint_handler(sig, frame):
    logger.info('SIGINT received...')
    raise KeyboardInterrupt()


def sigterm_handler(sig, frame):
    logger.info('SIGTERM received...')
    raise KeyboardInterrupt()


def init_chaos_executors() -> Dict[str, ChaosCommandExecutor]:
    proc_manager = ProcessManager()
    stress_ng_executor = StressNgCommandExecutor(proc_manager)
    return {
        'stress-ng': stress_ng_executor
    }


def main():
    listener = create_listener()

    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigterm_handler)

    if listener is None:
        logger.error(f'Unknown listener type `{os.environ.get("edgechaos_listener_type")}` set')
        return

    chaos_executors = init_chaos_executors()
    chaos_daemon = EdgeChaosDaemon(listener, chaos_executors)
    try:
        chaos_daemon.run()
    finally:
        chaos_daemon.stop()


if __name__ == '__main__':
    main()
