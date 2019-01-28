import logging
import math
import random
import time
from datetime import datetime, timedelta

import freesound
import giphy_client
from pixabay import Image
import requests
from giphy_client.rest import ApiException

from googleapiclient.discovery import build
from pafy import pafy
from tqdm import tqdm

import config

logger = logging.getLogger(__name__)


class Downloader(object):
    def __init__(self, key, download_path, download_num, id):
        self.key = key
        self.download_path = download_path
        self.download_num = download_num
        self.id = id
        self.tags = []

    @staticmethod
    def downloader(url, download_path):
        # Streaming, so we can iterate over the response.
        r = requests.get(url, stream=True)
        # Total size in bytes.
        total_size = int(r.headers.get('content-length', 0))
        block_size = 1024
        total_bytes = math.ceil(total_size // block_size)
        progress = 0

        with open(download_path, 'wb') as f:
            for data in tqdm(r.iter_content(block_size), total=total_bytes,
                             unit='B', bar_format='{percentage:3.0f}%'):
                f.write(data)
                progress += 1
                percent_downloaded = round((progress / total_bytes) * 100)
                if config.GLOBAL_DOWNLOAD_TRACKER != percent_downloaded:
                    if percent_downloaded > 100:
                        config.GLOBAL_DOWNLOAD_TRACKER = 100
                    else:
                        config.GLOBAL_DOWNLOAD_TRACKER = percent_downloaded
                    end_point = config.BASE_URL + '/script/1/'
                    requests.patch(end_point, json={
                        'download': config.GLOBAL_DOWNLOAD_TRACKER,
                    })
                    time.sleep(.1)

        f.close()

    def generate_keyword(self):
        word_url = 'https://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain'
        response = requests.get(word_url)
        words = response.content.splitlines()
        word = words[random.randint(0, len(words) - 1)].decode('utf-8')
        self.tags.append(word)
        return word

    def store(self, url, media):
        end_point = self._url('/content/')
        requests.post(end_point, json={
            'litter_id': self.id,
            'url': url,
            'type': media,
        })

    @staticmethod
    def _url(path):
        return config.BASE_URL + path

    def reset(self):
        del self.tags[:]


class VidDownloader(Downloader):
    def __init__(self, key, download_path, download_num, id):
        super(VidDownloader, self).__init__(key, download_path, download_num, id)
        self.interval_lst = []

    def download(self):
        logger.warning('downloading videos')

        def url(video):
            return 'https://www.youtube.com/watch?v=' + video.videoid

        used = []
        id_lst = self.get_vid_ids()
        i = 0
        while i < self.download_num:
            index = random.randint(0, len(id_lst) - 1)
            if index not in used:
                used.append(index)
                video = pafy.new(id_lst[index]['id'])
                duration = datetime.strptime(video.duration, '%H:%M:%S')

                if 20 > duration.minute > 0:
                    interval = self.generate_interval(video, duration)
                    self.interval_lst.append(interval)
                    print('starting to download new video')
                    video.getbest(preftype='mp4').download(self.download_path, quiet=True, meta=True,
                                                           callback=self.download_handler)
                    self.store(url(video), 'vid')
                    i += 1

    def get_vid_ids(self):
        id_lst = []
        YOUTUBE_API_SERVICE_NAME = 'youtube'
        YOUTUBE_API_VERSION = 'v3'
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=self.key)

        while len(id_lst) != (self.download_num * 5):
            search = self.generate_keyword()
            search_response = youtube.search().list(q=search, part='id, snippet', type='video').execute()
            for result in search_response.get('items', []):
                video_id = {'id': result['id']['videoId']}
                id_lst.append(video_id)
        return id_lst

    def generate_interval(self, video, duration):
        cuts = [3, 5, 7, 10, 12]
        start_minute = random.randint(0, duration.minute - 1)
        start_second = random.randint(0, 59)
        interval = random.choice(cuts)
        return self.valid_interval(video.title, duration, start_minute, start_second, interval)

    @staticmethod
    def valid_interval(title, duration, minute, second, interval):
        time_string = '0:' + str(minute) + ':' + str(second)
        start = datetime.strptime(time_string, '%H:%M:%S')
        end = start + timedelta(0, interval)

        # verify we are bounded by the video duration
        if end > duration:
            end = start - timedelta(0, interval)
            return title, end.strftime('%H:%M:%S'), start.strftime('%H:%M:%S')
        else:
            return title, start.strftime('%H:%M:%S'), end.strftime('%H:%M:%S')

    @staticmethod
    def download_handler(total_bytes_in_stream, total_bytes_downloaded, ratio_downloaded, download_rate, eta):
        #print('handling download')
        percent_downloaded = round(int(ratio_downloaded * 100))
        if config.GLOBAL_DOWNLOAD_TRACKER != percent_downloaded:
            config.GLOBAL_DOWNLOAD_TRACKER = percent_downloaded
            end_point = config.BASE_URL + '/script/1/'
            requests.patch(end_point, json={
                'download': percent_downloaded,
            })
        else:
            return None


class GifDownloader(Downloader):
    def __init__(self, key, download_path, download_num, id):
        super(GifDownloader, self).__init__(key, download_path, download_num, id)

    def download(self):
        logger.warning('downloading gifs')

        def generate_rating():
            choice = random.randint(0, 2)
            if choice == 0:
                return 'g'
            elif choice == 1:
                return 'pg'
            else:
                return 'pg-13'

        api = giphy_client.DefaultApi()
        limit = 50
        offset = 0
        rating = generate_rating()
        lang = 'en'
        fmt = 'json'
        i = 0

        while i < self.download_num:
            search = self.generate_keyword()
            try:
                response = api.stickers_search_get(self.key, search, limit=limit, offset=offset,
                                                   rating=rating, lang=lang, fmt=fmt)
                response_count = len(response.data)
                if response_count:
                    index = random.randint(0, response_count - 1)
                    url = response.data[index].images.original.url
                    gif_path = self.download_path + str(i) + '.gif'
                    self.downloader(url, gif_path)
                    self.store(url, 'gif')
                    i += 1
            except ApiException as e:
                logger.error("Exception when calling DefaultApi->stickers_random_get: %s\n" % e)


class PicDownloader(Downloader):
    def __init__(self, key, download_path, download_num, id):
        super(PicDownloader, self).__init__(key, download_path, download_num, id)

    def download(self):
        logger.warning('downloading pictures')

        pix = Image(self.key)
        i = 0
        while i < self.download_num:
            search = self.generate_keyword()
            img_search = pix.search(q=search, page=1, per_page=30)
            hits = len(img_search['hits'])

            if hits:
                index = random.randint(0, hits - 1)
                url = img_search['hits'][index]['webformatURL']
                pic_path = self.download_path + str(i) + '.jpg'
                self.downloader(url, pic_path)
                self.store(url, 'pic')
                i += 1
            time.sleep(2)


class SfxDownloader(Downloader):
    def __init__(self, key, download_path, download_num, id):
        super(SfxDownloader, self).__init__(key, download_path, download_num, id)

    def download(self):
        logger.warning('downloading sfx')
        client = freesound.FreesoundClient()
        client.set_token(self.key)
        i = 0

        while i < self.download_num:
            try:
                response = client.get_sound(random.randint(0, 96451))
                url = response.url
                name = str(i) + '.mp3'
                response.retrieve_preview(self.download_path, name=name)
                self.store(url, 'sfx')
                i += 1
            except Exception as e:
                print(e)

