import os
import time
import requests

import config
from ContentManager import ContentManager
from ContentUploader import ContentUploader

logger = config.set_logger()


class LitterBug(object):
    def __init__(self):
        self.ContentManager = ContentManager()
        self.ContentUploader = ContentUploader(self.ContentManager.name, self.ContentManager.id,
                                               self.ContentManager.result_path)
        self.status = self.set_status('Initialized...')

    def generate_clip(self):
        logger.info('Generating clip...')
        self.download_content()
        self.create_clip()
        self.download_clip()

    def download_content(self):
        self.set_status('Downloading content...')
        self.ContentManager.VidDownloader.download()
        self.ContentManager.GifDownloader.download()
        self.ContentManager.PicDownloader.download()
        self.ContentManager.SfxDownloader.download()

    def create_clip(self):
        logger.info('Creating clip...')
        self.set_status('Randomizing content...')
        self.ContentManager.ClipEditor.set_interval_lst(self.ContentManager.VidDownloader.interval_lst)
        self.ContentManager.ClipEditor.create_clip()

    def download_clip(self):
        logger.info('Downloading clip...')
        self.set_status('Downloading newly generated content...')
        self.ContentManager.ClipEditor.download_result()

    def upload_clip(self):
        logger.info('Uploading clip...')
        self.set_status('Uploading newly generated content...')
        time.sleep(5)
        self.ContentManager.retrieve_tags()
        self.ContentUploader.set_tags(self.ContentManager.tags)
        self.ContentUploader.upload_content()

    def clean_up(self):
        logger.info('Cleaning up...')
        self.set_status('Preparing to generate more content...')
        self.clear_folder(config.VID_PATH)
        self.clear_folder(config.GIF_PATH)
        self.clear_folder(config.PIC_PATH)
        self.clear_folder(config.SFX_PATH)
        self.clear_file(self.ContentManager.result_path)
        time.sleep(5)

    def exception_handler(self):
        logger.info('Handling exception...')
        self.set_status('Something went wrong...')
        config.GLOBAL_DOWNLOAD_TRACKER = 100
        end_point = self._url('/script/1/')
        requests.patch(end_point, json={
            'download': config.GLOBAL_DOWNLOAD_TRACKER,
        })
        time.sleep(5)

    def set_status(self, status):
        self.status = status
        task = {'status': self.status}
        url = self._url('/script/1/')
        return requests.patch(url, json=task)

    @staticmethod
    def clear_folder(folder):
        logger.info('Clearing folder: ' + folder)
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)

    @staticmethod
    def clear_file(path):
        logger.info('Clearing file: ' + path)
        if os.path.exists(path):
            os.remove(path)

    @staticmethod
    def _url(path):
        return config.BASE_URL + path
