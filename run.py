import logging
import subprocess

import  config

litter_bug = ['python3',
              config.BASE_PATH + 'main.py']

if __name__ == '__main__':
    logging.warning('starting run of litter bug script...')
    while True:
        try:
            logging.warning('attempting to run litter bug as subprocess')
            subprocess.Popen(litter_bug, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).wait()
        except subprocess.CalledProcessError as e:
            logging.error(e)
