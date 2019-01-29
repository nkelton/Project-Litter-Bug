import logging
import subprocess
import sys

import config

litter_bug = ['python3', config.BASE_PATH + 'main.py']

logging.basicConfig(filename=config.LOG, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.warning('starting run of litter bug script...')
    while True:
        try:
            logger.warning('attempting to run litter bug as subprocess')
            subprocess.Popen(litter_bug, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).wait()
        except subprocess.CalledProcessError as e:
            logger.warning('Error has occurred in run.py')
            logger.error(e)
