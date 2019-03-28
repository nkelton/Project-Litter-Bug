import glob
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


def clear_mp3_files():
    logger.info('Clearning mp3 files: ' + config.BASE_PATH)
    file_lst = glob.glob(os.path.join(config.BASE_PATH, "*.mp3"))
    for f in file_lst:
        os.remove(f)


def clear_content_from_db(litter_id):
    logger.info('Clearing unused content from database...')
    return requests.delete(config.BASE_URL + '/content/' + litter_id + '/', auth=config.AUTH)


def clear_file(path):
    logger.info('Clearing file: ' + path)
    if os.path.exists(path):
        os.remove(path)


def update_script(task):
    url = config.BASE_URL + '/script/1/'
    return requests.patch(url, json=task, auth=config.AUTH)


def generate_keyword():
    logger.info('Generating keyword...')
    word_url = 'https://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain'
    response = requests.get(word_url)
    words = response.content.splitlines()
    word = words[random.randint(0, len(words) - 1)].decode('utf-8')
    return word


def get_current_download_value():
    url = config.BASE_URL + '/script/1/'
    response = requests.get(url, auth=config.AUTH)
    script_data = response.json()
    return script_data['download']


def is_stalling(download_tracker):
    if download_tracker == get_current_download_value():
        return True
    else:
        return False


def wait_timeout_interval(proc, seconds, interval):
    """Wait for a process to finish, or raise exception after timeout"""
    logger.info('Waiting or timing out with interval...')
    start = time.time()
    end = start + seconds
    wait = interval
    config.TIMEOUT_DOWNLOAD_TRACKER = 'initialized'

    while True:
        result = proc.poll()
        if result is not None:
            return result
        if time.time() >= end or is_stalling(config.TIMEOUT_DOWNLOAD_TRACKER):
            logger.warning('Process has timed out')
            proc.kill()
            return None
        config.TIMEOUT_DOWNLOAD_TRACKER = get_current_download_value()
        time.sleep(wait)


def wait_timeout(proc, seconds):
    """Wait for a process to finish, or raise exception after timeout"""
    logger.info('Waiting or timing out...')
    start = time.time()
    end = start + seconds
    interval = min(seconds / 1000.0, .25)

    while True:
        result = proc.poll()
        if result is not None:
            return result
        if time.time() >= end:
            logger.warning('Process has timed out')
            proc.kill()
            return None
        time.sleep(interval)


def wait_timeout_extended(proc, seconds, interval):
    """Wait for a process to finish, or raise exception after timeout"""
    logger.info('Waiting or timing out with interval...')
    start = time.time()
    end = start + seconds
    wait = interval

    while True:
        result = proc.poll()
        if result is not None:
            return result
        if time.time() >= end:
            logger.warning('Process has timed out')
            proc.kill()
            return None
        config.TIMEOUT_DOWNLOAD_TRACKER = get_current_download_value()
        time.sleep(wait)
