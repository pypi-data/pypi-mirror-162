import logging
from typing import Dict

from edgechaos.executor.api import ChaosCommandExecutor, ChaosCommand
from edgechaos.listeners.api import ChaosCommandListener

logger = logging.getLogger(__name__)


class EdgeChaosDaemon:

    def __init__(self, chaos_listener: ChaosCommandListener, chaos_executors: Dict[str,ChaosCommandExecutor]):
        self.chaos_listener = chaos_listener
        self.chaos_executors = chaos_executors
        self.running = False

    def run(self):
        logger.info('Start edge chaos daemon...')
        self.running = True
        try:
            for cmd in self.chaos_listener.listen():
                if not self.running:
                    break
                logger.debug(f'Received command: {cmd}')
                self.execute(cmd)
        except Exception as e:
            logger.error(e)
        finally:
            logger.info('Stopping edge chaos daemon...')
            self.stop()

    def execute(self,cmd: ChaosCommand):
        executor = self.chaos_executors.get(cmd.name)
        if executor is None:
            logger.error(f'Received unknown chaos command type: {cmd.name}.')
            return

        if cmd.kind == 'start':
            executor.start_command(cmd)
        elif cmd.kind == 'stop':
            executor.stop_command(cmd)
        else:
            logger.error(f'Received unknown chaos command kind: {cmd.kind}.t')


    def stop(self):
        if self.running:
            self.running = False
            self.chaos_listener.stop()
            for executor in self.chaos_executors.values():
                executor.stop()
