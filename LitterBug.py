import random
import time
import subprocess

import ClipEditor
import Downloaders
import config
import utils
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

        logger.info('Vid num: ' + str(self.vid_num))
        logger.info('Gif num: ' + str(self.gif_num))
        logger.info('Pic num: ' + str(self.pic_num))
        logger.info('Sfx num: ' + str(self.sfx_num))

        self.result_path = config.RESULT_PATH + self.name
        self.tags = None

        self.vid_downloader = Downloaders.VidDownloader(self.id, self.vid_num)
        self.gif_downloader = Downloaders.GifDownloader(self.id, self.gif_num)
        self.pic_downloader = Downloaders.PicDownloader(self.id, self.pic_num)
        self.sfx_downloader = Downloaders.SfxDownloader(self.id, self.sfx_num)

        self.content_uploader = ContentUploader(self.name, self.id, self.result_path)

    def generate_id(self):
        id = random.getrandbits(63)
        task = {'litter_id': id}
        utils.update_script(task)
        return id

    def generate_clip(self):
        logger.info('Generating clip...')
        self.download_content()
        self.create_clip()

    def download_content(self):
        logger.info('Downloading content...')
        self.set_status('Downloading content...')
        self.vid_downloader.download()
        self.gif_downloader.download()
        self.pic_downloader.download()
        self.sfx_downloader.download()

    def create_clip(self):
        logger.info('Creating clip...')
        self.set_status('Creating new content...')
        str_lst = str(self.vid_downloader.interval_lst)
        interval_lst = str_lst.replace(",", "*")
        args_lst = [str(self.vid_num), str(self.gif_num), str(self.pic_num),
                   str(self.sfx_num), self.result_path, interval_lst]
        args = ','.join("{0}".format(arg) for arg in args_lst)
        cmd = ['runp', 'ClipEditor.py', 'create:'+args]
        p = subprocess.Popen(cmd)
        pid = utils.wait_timeout_interval(p, config.CREATE_TIMEOUT, config.CREATE_INTERVAL)
        if pid is None:
           raise Exception('Clip creation has timed out...')

    def upload_clip(self):
        logger.info('Uploading clip...')
        self.set_status('Uploading new content...')
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
        utils.clear_mp3_files()
        time.sleep(5)

    def exception_handler(self):
        logger.info('Handling exception...')
        self.set_status('Something went wrong...')
        config.GLOBAL_DOWNLOAD_TRACKER = 100
        task = {'download': config.GLOBAL_DOWNLOAD_TRACKER }
        utils.update_script(task)
        utils.clear_content_from_db(self.id)
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

