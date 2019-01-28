# TODO: refactor for Python3
import logging

from LitterBug import LitterBug

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
        logger.warning('Exception occured at mainy.py')
        logger.error(e)
        logger.warning('attempting to handle exception')
        lb.exception_handler()

    lb.clean_up()
