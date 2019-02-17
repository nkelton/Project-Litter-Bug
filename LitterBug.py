import random
import time
import subprocess

import Downloaders
import config
import utils
from ClipEditor import ClipEditor
from ContentUploader import ContentUploader

logger = config.set_logger('LitterBug.py')


class LitterBug(object):
    def __init__(self):
        self.id = self.generate_id()
        self.name = 'plb-' + str(self.id) + '.mp4'

        self.vid_num = random.randint(2, 5)
        self.gif_num = random.randint(3, 9)
        self.pic_num = random.randint(3, 9)
        self.sfx_num = random.randint(3, 9)

        self.result_path = config.RESULT_PATH + self.name
        self.tags = None

        self.vid_downloader = Downloaders.VidDownloader(self.id, self.vid_num)
        self.gif_downloader = Downloaders.GifDownloader(self.id, self.gif_num)
        self.pic_downloader = Downloaders.PicDownloader(self.id, self.pic_num)
        self.sfx_downloader = Downloaders.SfxDownloader(self.id, self.sfx_num)

        self.content_uploader = ContentUploader(self.name, self.id, self.result_path)

    def generate_id(self):
        id = random.getrandbits(63)
        task = {'litter_id': self.id}
        utils.update_script(task)
        return id

    def generate_clip(self):
        logger.info('Generating clip...')
        self.download_content()
        self.create_clip()

    def download_content(self):
        self.set_status('Downloading content...')
        self.vid_downloader.download()
        self.gif_downloader.download()
        self.pic_downloader.download()
        self.sfx_downloader.download()

    def create_clip(self):
        self.set_status('Generating content...')
        logger.info('Creating clip...')
        str_lst = str(self.vid_downloader.interval_lst)
        interval_lst = str_lst.replace(",", "*")
        args_lst = [str(self.vid_num), str(self.gif_num), str(self.pic_num),
                    str(self.sfx_num), self.result_path, interval_lst]
        args = ','.join("{0}".format(arg) for arg in args_lst)
        cmd = ['runp', 'ClipEditor.py', 'create:'+args]
        p = subprocess.Popen(cmd)
        utils.wait_timeout(p, config.CREATION_TIMEOUT)

    def upload_clip(self):
        logger.info('Uploading clip...')
        self.set_status('Uploading newly generated content...')
        time.sleep(5)
        self.retrieve_tags()
        self.content_uploader.set_tags(self.tags)
        self.content_uploader.upload_content()

    def clean_up(self):
        logger.info('Cleaning up...')
        self.set_status('Preparing to generate more content...')
        utils.clear_folder(config.VID_PATH)
        utils.clear_folder(config.GIF_PATH)
        utils.clear_folder(config.PIC_PATH)
        utils.clear_folder(config.SFX_PATH)
        utils.clear_file(self.result_path)
        time.sleep(5)

    def exception_handler(self):
        logger.info('Handling exception...')
        self.set_status('Something went wrong...')
        config.GLOBAL_DOWNLOAD_TRACKER = 100
        task = {'download': config.GLOBAL_DOWNLOAD_TRACKER }
        utils.update_script(task)
        time.sleep(5)

    def retrieve_tags(self):
        logger.info('Retrieving tags...')
        self.tags = 'plb, project litter bug, random content generator,'
        for tag in self.vid_downloader.tags:
            self.tags += str(' ' + tag + ',')
        for tag in self.gif_downloader.tags:
            self.tags += str(' ' + tag + ',')
        for tag in self.pic_downloader.tags:
            self.tags += str(' ' + tag + ',')
        self.tags = self.tags[:-1]

    @staticmethod
    def set_status(status):
        task = {'status': status}
        utils.update_script(task)
