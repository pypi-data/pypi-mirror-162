import logging
import subprocess

from edgechaos.executor.api import ChaosCommandExecutor, ChaosCommand

logger = logging.getLogger(__name__)


class TcCommandExecutor(ChaosCommandExecutor):

    def start_command(self, command: ChaosCommand):
        self._run_tc_cmd(command)

    def _run_tc_cmd(self, command: ChaosCommand):
        parameters = command.parameters.get("tc")
        if parameters is None:
            logger.warning(f'Received tc command ({command}) has no parameters stored. Nothing happens...')
        cmd = ['tc'] + parameters
        subprocess.Popen(cmd)

    def stop_command(self, command: ChaosCommand):
        # Currently we do not look into the content of the cmd at all and just run tc with supplied  parameters
        # That means it is up to the clients to send the right command with the stop event.
        # Users could also delete a tc rule sending a start command - it currently does not matter
        self._run_tc_cmd(command)

    def stop(self):
        super().stop()
