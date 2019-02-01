import random
import requests
import config
from ClipEditor import ClipEditor
from Downloaders import VidDownloader, GifDownloader, PicDownloader, SfxDownloader

logger = config.set_logger()


class ContentManager(object):
    def __init__(self):
        self.id = self.create_id()
        self.name = self.create_name()
        self.tags = None

        self.result_path = config.RESULT_PATH + self.name

        self.vid_num = random.randint(3, 6)
        self.gif_num = random.randint(3, 9)
        self.pic_num = random.randint(3, 9)
        self.sfx_num = random.randint(3, 9)

        self.VidDownloader = VidDownloader(config.YOUTUBE_API_KEY, config.VID_PATH, self.vid_num, self.id)
        self.GifDownloader = GifDownloader(config.GIPHY_API_KEY, config.GIF_PATH, self.gif_num, self.id)
        self.PicDownloader = PicDownloader(config.YOUTUBE_API_KEY, config.VID_PATH, self.pic_num, self.id)
        self.SfxDownloader = SfxDownloader(config.YOUTUBE_API_KEY, config.VID_PATH, self.sfx_num, self.id)

        self.ClipEditor = ClipEditor(self.vid_num, self.gif_num, self.pic_num, self.sfx_num, self.result_path)

    def retrieve_tags(self):
        logger.info('Retrieving tags...')
        self.tags = 'plb, project litter bug, random content generator,'
        for tag in self.VidDownloader.tags:
            self.tags += str(' ' + tag + ',')
        for tag in self.GifDownloader.tags:
            self.tags += str(' ' + tag + ',')
        for tag in self.PicDownloader.tags:
            self.tags += str(' ' + tag + ',')
        self.tags = self.tags[:-1]

    def create_id(self):
        self.id = random.getrandbits(63)
        task = {'litter_id': self.id}
        url = self._url('/script/1/')
        requests.patch(url, json=task)
        return self.id

    @staticmethod
    def _url(path):
        return config.BASE_URL + path

    def create_name(self):
        return 'plb-' + str(self.id) + '.mp4'
