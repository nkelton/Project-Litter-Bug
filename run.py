import logging
import subprocess
import sys

import config
from utils import wait_timeout, wait_timeout_extended

litter_bug = ['python3', config.BASE_PATH + 'main.py']

logger = config.set_logger('run.py')

if __name__ == '__main__':
    logger.info('BEGINNING OF LITTER BUG SCRIPT RUN.PY...')
    while True:
        try:
            logger.info('LAUNCHING NEW LITTER BUG...')
            p = subprocess.Popen(litter_bug, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            wait_timeout_extended(p, config.LITTER_BUG_TIMEOUT, config.LITTER_BUG_INTERVAL)
        except subprocess.CalledProcessError as e:
            logger.error('Error has occurred in run.py')
            logger.error(e)
