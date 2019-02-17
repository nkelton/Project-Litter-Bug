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
        self.id = self.generate_id
        self.name = 'plb-' + str(self.id) + '.mp4'

        self.vid_num = random.randint(2, 5)
        self.gif_num = random.randint(3, 9)
        self.pic_num = random.randint(3, 9)
        self.sfx_num = random.randint(3, 9)

        self.tags = None
        self.result_path = config.RESULT_PATH + self.name

        self.vidDownloader = Downloaders.VidDownloader(self.id, self.vid_num)
        self.gifDownloader = Downloaders.GifDownloader(self.id, self.gif_num)
        self.picDownloader = Downloaders.PicDownloader(self.id, self.pic_num)
        self.sfxDownloader = Downloaders.SfxDownloader(self.id, self.sfx_num)

        self.ContentUploader = ContentUploader(self.name, self.id, self.result_path)
        self.ClipEditor = ClipEditor(self.vid_num, self.gif_num, self.pic_num, self.sfx_num, self.result_path)

    def generate_id(self):
        id = random.getrandbits(63)
        task = {'litter_id': self.id}
        utils.update_script(task)
        return id

    def generate_clip(self):
        logger.info('Generating clip...')
        self.download_content()
        self.create_clip()
        self.download_clip()

    def download_content(self):
        self.set_status('Downloading content...')
        self.vidDownloader.download()
        self.gifDownloader.download()
        self.picDownloader.download()
        self.sfxDownloader.download()

    def download(self, content_type, timeout):
        if type == 'VID':
            self.vidDownloader.download()
        else:
            if content_type == 'GIF':
                cmd = ['runp', 'Downloaders.py', 'download_gif:',
                       'litter_id=' + str(self.id), 'key=' + config.GIPHY_API_KEY,
                       'download_path=' + config.GIF_PATH]
            elif content_type == 'PIC':
                cmd = ['runp', 'Downloaders.py', 'download_pic:',
                       'litter_id=' + str(self.id), 'key=' + config.PIXABAY_API_KEY,
                       'download_path=' + config.PIC_PATH]
            elif content_type == 'SFX':
                cmd = ['runp', 'Downloaders.py', 'download_sfx:',
                       'litter_id=' + str(self.id), 'key=' + config.FREESOUND_API_KEY,
                       'download_path=' + config.SFX_PATH]
            else:
                cmd = None

            if cmd is not None:
                p = subprocess.Popen(cmd)
                utils.wait_timeout(p, timeout)

    def create_clip(self):
        logger.info('Creating clip...')
        self.set_status('Randomizing content...')
        self.ClipEditor.set_interval_lst(self.vidDownloader.interval_lst)
        self.ClipEditor.create_clip()

    def download_clip(self):
        logger.info('Downloading clip...')
        self.set_status('Downloading newly generated content...')
        self.ClipEditor.download_result()

    def upload_clip(self):
        logger.info('Uploading clip...')
        self.set_status('Uploading newly generated content...')
        time.sleep(5)
        self.retrieve_tags()
        self.ContentUploader.set_tags(self.tags)
        self.ContentUploader.upload_content()

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
        for tag in self.vidDownloader.tags:
            self.tags += str(' ' + tag + ',')
        for tag in self.gifDownloader.tags:
            self.tags += str(' ' + tag + ',')
        for tag in self.picDownloader.tags:
            self.tags += str(' ' + tag + ',')
        self.tags = self.tags[:-1]

    @staticmethod
    def set_status(status):
        task = {'status': status}
        utils.update_script(task)
