# TODO: refactor for Python3
import logging

from LitterBug import LitterBug

if __name__ == '__main__':
    logging.warning('attempting to initalize lb')
    lb = LitterBug()

    try:
        logging.warning('attempting to generate clip')
        lb.generate_clip()
        logging.warning('attempting to upload clip')
        lb.upload_clip()

    except Exception as e:
        logging.warning('Exception occured at mainy.py')
        logging.error(e)
        logging.warning('attempting to handle exception')
        lb.exception_handler()

    lb.clean_up()
