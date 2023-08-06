import logging
import subprocess
from typing import List

logger = logging.getLogger(__name__)


def convert_args_to_key(args: List[str]) -> str:
    return ' '.join(args)


class ProcessManager():

    def __init__(self):
        self.processes = {}

    def start_process(self, args: List[str]):
        proc = subprocess.Popen(args)
        key = convert_args_to_key(args)
        logger.debug(f'Start process: {key}')
        self.processes[key] = proc

    def kill_process(self, args: List[str]):
        key = convert_args_to_key(args)
        logger.debug(f'Kill process: {key}')
        self.processes[key].kill()
        del self.processes[key]

    def stop(self):
        logger.info('ProcessManager stops and kills all remaining processes...')
        for value in self.processes:
            value.kill()

