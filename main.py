# TODO: refactor for Python3
import logging

import config
from LitterBug import LitterBug

logging.basicConfig(filename=config.LOG, format='%(asctime)s %(levelname)-8s %(name)-15s %(message)s')
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.warning('attempting to initalize lb')
    lb = LitterBug()

    try:
        logger.warning('attempting to generate clip')
        lb.generate_clip()
        logger.warning('attempting to upload clip')
        lb.upload_clip()

    except Exception as e:
        logger.warning('Exception occured at main.py')
        logger.error(e)
        logger.warning('attempting to handle exception')
        lb.exception_handler()

    lb.clean_up()
