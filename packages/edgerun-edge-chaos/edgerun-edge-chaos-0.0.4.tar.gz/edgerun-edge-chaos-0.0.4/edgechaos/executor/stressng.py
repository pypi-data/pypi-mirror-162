import logging
from typing import List

from edgechaos.executor.api import ChaosCommandExecutor, ChaosCommand
from edgechaos.util.process import ProcessManager

logger = logging.getLogger(__name__)


def convert_cmd_to_args(cmd: ChaosCommand) -> List[str]:
    args = ['stress-ng']
    for key, value in cmd.parameters.items():
        args.append(f'--{key}')
        args.append(str(value))
    return args


class StressNgCommandExecutor(ChaosCommandExecutor):

    def __init__(self, process_manager: ProcessManager):
        self.process_manager = process_manager

    def start_command(self, command: ChaosCommand):
        logger.info(f'StressNgCommandExecutor executes following command {command}')
        args = convert_cmd_to_args(command)
        self.process_manager.start_process(args)

    def stop_command(self, command: ChaosCommand):
        logger.info(f'StressNgCommandExecutor stops following command {command}')
        args = convert_cmd_to_args(command)
        self.process_manager.kill_process(args)

    def stop(self):
        logger.info('Stopping StressNgCommandExecutor... ')
        self.process_manager.stop()