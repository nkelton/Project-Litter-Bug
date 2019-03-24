import config
import googlecloudprofiler
import subprocess
from utils import wait_timeout, wait_timeout_extended

logger = config.set_logger('run.py')


def main():
    # set_cloud_profiler()
    logger.info('BEGINNING OF LITTER BUG SCRIPT RUN.PY...')
    litter_bug = ['python3', config.BASE_PATH + 'main.py']

    while True:
        try:
            logger.info('LAUNCHING NEW LITTER BUG...')
            p = subprocess.Popen(litter_bug, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            wait_timeout_extended(p, config.LITTER_BUG_TIMEOUT, config.LITTER_BUG_INTERVAL)
        except subprocess.CalledProcessError as e:
            logger.error('Error has occurred in run.py')
            logger.error(e)


# def set_cloud_profiler():
#     logger.info("Setting cloud profiler...")
#     try:
#         googlecloudprofiler.start(
#             service='plb-profiler',
#             service_version='1.0.1',
#             verbose=3,
#         )
#     except (ValueError, NotImplementedError) as exc:
#         print(exc)  # Handle errors here


if __name__ == '__main__':
    main()

