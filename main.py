# TODO: refactor for Python3
import logging

from LitterBug import LitterBug

if __name__ == '__main__':
    logging.info('attempting to initalize lb')
    lb = LitterBug()

    try:
        logging.info('attempting to generate clip')
        lb.generate_clip()
        logging.info('attempting to upload clip')
        lb.upload_clip()

    except Exception as e:
        logging.error(e)
        logging.info('attempting to handle exception')
        lb.exception_handler()

    lb.clean_up()
