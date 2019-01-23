import logging
import subprocess

import  config

litter_bug = ['python3',
              config.BASE_PATH + 'main.py']

if __name__ == '__main__':
    logging.info('starting run of litter bug script...')
    while True:
        try:
            logging.info('attempting to run litter bug as subprocess')
            proc = subprocess.Popen(litter_bug, stderr=subprocess.STDOUT)
            proc.wait()
        except subprocess.CalledProcessError as e:
            logging.error(e)
