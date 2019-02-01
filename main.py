import config
from LitterBug import LitterBug

logger = config.set_logger()

if __name__ == '__main__':
    logger.info('INITIALIZING LITTER BUG... ')
    lb = LitterBug()

    try:
        lb.generate_clip()
        lb.upload_clip()

    except Exception as e:
        logger.warning('Exception occured at main.py')
        logger.error(e)
        lb.exception_handler()

    lb.clean_up()
