import logging
import os
import time
import requests

import config
from ContentManager import ContentManager
from ContentUploader import ContentUploader

logging.basicConfig(filename=config.LOG, format='%(asctime)s %(levelname)-8s %(name)-15s %(message)s')
logger = logging.getLogger(__name__)


#TODO: faciliate name, id, and video path within Litter Bug, since values belong to both ContentManager and ContentUploader
class LitterBug(object):
    def __init__(self):
        self.ContentManager = ContentManager()
        self.ContentUploader = ContentUploader(self.ContentManager.name, self.ContentManager.result_path, self.ContentManager.id)
        self.status = self.set_status('Initialized...')

    def generate_clip(self):
        logger.warning('attempting to download content')
        self.download_content()
        logger.warning('attempting to create clip')
        self.create_clip()
        logger.warning('attempting to download clip')
        self.download_clip()

    def download_content(self):
        self.set_status('Downloading content...')
        self.ContentManager.VidDownloader.download()
        self.ContentManager.GifDownloader.download()
        self.ContentManager.PicDownloader.download()
        self.ContentManager.SfxDownloader.download()

    def create_clip(self):
        self.set_status('Randomizing content...')
        self.ContentManager.ClipEditor.set_interval_lst(self.ContentManager.VidDownloader.interval_lst)
        self.ContentManager.ClipEditor.create_clip()

    def download_clip(self):
        self.set_status('Downloading newly generated content...')
        self.ContentManager.ClipEditor.download_result()

    def upload_clip(self):
        self.set_status('Uploading newly generated content...')
        time.sleep(5)
        self.ContentManager.retrieve_tags()
        self.ContentUploader.set_tags(self.ContentManager.tags)
        self.ContentUploader.upload_content()

    def clean_up(self):
        logger.warning('attempting to clean up')
        self.set_status('Preparing to generate more content...')
        self.clear_folder(self.ContentManager.vid_path)
        self.clear_folder(self.ContentManager.gif_path)
        self.clear_folder(self.ContentManager.pic_path)
        self.clear_folder(self.ContentManager.sfx_path)
        self.clear_file(self.ContentManager.result_path)
        time.sleep(5)

    def exception_handler(self):
        logger.warning('handling exception')
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
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)

    @staticmethod
    def clear_file(path):
        if os.path.exists(path):
            os.remove(path)

    @staticmethod
    def _url(path):
        return config.BASE_URL + path
