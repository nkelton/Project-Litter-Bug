import random
import requests
import config
from ClipEditor import ClipEditor
from Downloaders import VidDownloader, GifDownloader, PicDownloader, SfxDownloader


class ContentManager(object):
    def __init__(self):
        self.id = self.create_id()
        self.name = self.create_name()
        self.tags = None

        self.vid_path = config.VID_PATH
        self.gif_path = config.GIF_PATH
        self.pic_path = config.PIC_PATH
        self.sfx_path = config.SFX_PATH
        self.logo_path = config.LOGO_PATH
        self.result_path = config.RESULT_PATH + self.name
        self.thumb_path = config.THUMB_PATH

        self.vid_num = random.randint(3,6)
        self.gif_num = random.randint(3,9)
        self.pic_num = random.randint(3,9)
        self.sfx_num = random.randint(3,9)

        self.VidDownloader = VidDownloader(config.YOUTUBE_API_KEY, self.vid_path, self.vid_num, self.id)
        self.GifDownloader = GifDownloader(config.GIPHY_API_KEY, self.gif_path, self.gif_num, self.id)
        self.PicDownloader = PicDownloader(config.PIXABAY_API_KEY, self.pic_path, self.pic_num, self.id)
        self.SfxDownloader = SfxDownloader(config.FREESOUND_API_KEY, self.sfx_path, self.sfx_num, self.id)

        self.ClipEditor = ClipEditor(self.vid_num, self.gif_num, self.pic_num, self.sfx_num,
                                     self.vid_path, self.gif_path, self.pic_path, self.sfx_path,
                                     self.logo_path, self.result_path, self.thumb_path)

    def retrieve_tags(self):
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
