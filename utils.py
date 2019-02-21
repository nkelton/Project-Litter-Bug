import os
import random
import time

import requests

import config

logger = config.set_logger('utils.py')


def clear_folder(folder):
    logger.info('Clearing folder: ' + folder)
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


def clear_file(path):
    logger.info('Clearing file: ' + path)
    if os.path.exists(path):
        os.remove(path)


def update_script(task):
    url = config.BASE_URL + '/script/1/'
    requests.patch(url, json=task)


def generate_keyword():
    logger.info('Generating keyword...')
    word_url = 'https://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain'
    response = requests.get(word_url)
    words = response.content.splitlines()
    word = words[random.randint(0, len(words) - 1)].decode('utf-8')
    logger.info('Random word: ' + word)
    return word


def get_current_download_value():
    logger.info('Getting download value...')
    url = config.BASE_URL + '/script/1/'
    response = requests.get(url)
    script_data = response.json()
    return script_data['download']


def recalc_wait_time(download_tracker, end, adjust):
    logger.info('Recalculating wait time...')
    current_download = get_current_download_value()
    if download_tracker != current_download:
        logger.info('Adding time...')
        end = end + adjust
    else:
        logger.info('Removing time...')
        end = end - adjust

    return current_download, end


def wait_timeout(proc, seconds, adjust, interval):
    """Wait for a process to finish, or raise exception after timeout"""
    logger.info('Waiting or timing out...')
    config.TIMEOUT_DOWNLOAD_TRACKER = 0
    start = time.time()
    end = start + seconds
    wait_interval = interval
    logger.info('Wait Interval:: ' + str(wait_interval))

    while True:
        result = proc.poll()
        if result is not None:
            return result
        if time.time() >= end:
            logger.warning('Process has timed out...')
            proc.kill()
            return None
        if time.time() < end:
            config.TIMEOUT_DOWNLOAD_TRACKER, end = recalc_wait_time(config.TIMEOUT_DOWNLOAD_TRACKER, end, adjust)

        logger.info('Current timeout value: ' + str(end))
        time.sleep(wait_interval)


