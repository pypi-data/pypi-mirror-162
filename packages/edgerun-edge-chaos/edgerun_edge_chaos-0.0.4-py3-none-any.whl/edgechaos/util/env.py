import logging
import os

logger = logging.getLogger(__name__)


def read_host_env():
    edgechaos_host = os.environ.get('edgechaos_host')

    if edgechaos_host is None:
        logger.info('edgechaos_host env variable not set, default to HOSTNAME')
        edgechaos_host = os.environ.get('HOSTNAME')
    return edgechaos_host
