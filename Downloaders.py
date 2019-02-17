import math
import random
import time
import subprocess
from datetime import datetime, timedelta

import freesound
import giphy_client
import requests
from giphy_client.rest import ApiException
from googleapiclient.discovery import build
from pafy import pafy
from pixabay import Image
from tqdm import tqdm

import config
import utils

logger = config.set_logger('Downloaders.py')


def store(litter_id, url, type):
    logger.info('Storing media...')
    end_point = config.BASE_URL + '/content/'
    requests.post(end_point, json={
        'litter_id': litter_id,
        'url': url,
        'type': type,
    })


def downloader(url, download_path):
        logger.info('Downloading...')
        r = requests.get(url, stream=True)
        total_size = int(r.headers.get('content-length', 0))
        block_size = 1024
        total_bytes = math.ceil(total_size // block_size)
        progress = 0

        with open(download_path, 'wb') as f:
            for data in tqdm(r.iter_content(block_size), total=total_bytes, unit='B'):
                f.write(data)
                progress += 1
                percent_downloaded = round((progress / total_bytes) * 100)
                if config.GLOBAL_DOWNLOAD_TRACKER != percent_downloaded:
                    if percent_downloaded > 100:
                        config.GLOBAL_DOWNLOAD_TRACKER = 100
                    else:
                        config.GLOBAL_DOWNLOAD_TRACKER = percent_downloaded
                        task = {'download': config.GLOBAL_DOWNLOAD_TRACKER}
                        utils.update_script(task)
                    time.sleep(.1)
        f.close()


class VidDownloader(object):
    def __init__(self, id, download_num):
        self.download_num = download_num
        self.interval_lst = []
        self.id = id
        self.tags = []

    def download(self):
        logger.info('Downloading videos...')
        id_lst = self.get_vid_ids(self.download_num)
        used = []
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
                    video.getbest(preftype='mp4').download(config.VID_PATH, quiet=True,
                                                           meta=True, callback=self.download_handler)
                    store(self.id, 'https://www.youtube.com/watch?v=' + video.videoid, 'vid')
                    i += 1

    def get_vid_ids(self, download_num):
        youtube = build(config.YOUTUBE_API_SERVICE_NAME, config.YOUTUBE_API_VERSION,
                        developerKey=config.YOUTUBE_API_KEY, cache_discovery=False)
        id_lst = []
        while len(id_lst) != (download_num * 5):
            search = utils.generate_keyword()
            search_response = youtube.search().list(q=search, part='id, snippet', type='video').execute()
            for result in search_response.get('items', []):
                video_id = {'id': result['id']['videoId']}
                id_lst.append(video_id)
                self.tags.append(search)
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
        percent_downloaded = round(int(ratio_downloaded * 100))
        if config.GLOBAL_DOWNLOAD_TRACKER != percent_downloaded:
            config.GLOBAL_DOWNLOAD_TRACKER = percent_downloaded
            task = {'download': percent_downloaded}
            utils.update_script(task)
        else:
            return None


class GifDownloader(object):
    def __init__(self, id, download_num):
        self.download_num = download_num
        self.id = id
        self.tags = []

    def download(self):
        logger.info('Downloading gifs...')
        api = giphy_client.DefaultApi()
        limit = 50
        offset = 0
        rating = ['g', 'pg', 'pg-13']
        lang = 'en'
        fmt = 'json'
        i = 0

        while i < self.download_num:
            search = utils.generate_keyword()
            try:
                response = api.stickers_search_get(config.GIPHY_API_KEY, search, limit=limit, offset=offset,
                                                   rating=rating[random.randint(0, 2)], lang=lang, fmt=fmt)
                response_count = len(response.data)
                if response_count:
                    index = random.randint(0, response_count - 1)
                    url = response.data[index].images.original.url
                    gif_path = config.GIF_PATH + str(i) + '.gif'
                    args = ','.join("{0}".format(arg) for arg in [url, gif_path])
                    cmd = ['runp', 'Downloaders.py', 'downloader:'+args]
                    p = subprocess.Popen(cmd)
                    utils.wait_timeout(p, config.GIPHY_TIMEOUT)
                    store(self.id, url, 'gif')
                    self.tags.append(search)
                    i += 1
            except ApiException as e:
                logger.error("Exception when calling DefaultApi->stickers_random_get: %s\n" % e)


class PicDownloader(object):
    def __init__(self, id, download_num):
        self.download_num = download_num
        self.id = id
        self.tags = []

    def download(self):
        logger.info('Downloading pics...')
        pix = Image(config.PIXABAY_API_KEY)
        i = 0

        while i < self.download_num:
            search = utils.generate_keyword()
            img_search = pix.search(q=search, page=1, per_page=30)
            hits = len(img_search['hits'])

            if hits:
                index = random.randint(0, hits - 1)
                url = img_search['hits'][index]['webformatURL']
                pic_path = config.PIC_PATH + str(i) + '.jpg'
                args = ','.join("{0}".format(arg) for arg in [url, pic_path])
                cmd = ['runp', 'Downloaders.py', 'downloader:'+args]
                p = subprocess.Popen(cmd)
                utils.wait_timeout(p, config.PIXABAY_TIMEOUT)
                store(self.id, url, 'pic')
                self.tags.append(search)
                i += 1
        time.sleep(1)


class SfxDownloader(object):
    def __init__(self, id, download_num):
        self.id = id
        self.tags = []
        self.download_num = download_num

    def download(self):
        logger.info('Downloading sfx...')
        args_lst = [str(self.id), config.GIPHY_API_KEY, config.SFX_PATH, str(self.download_num)]
        args = ','.join("{0}".format(arg) for arg in args_lst)
        logger.info('@@@@@@@@@ARGS:', args)
        cmd = ['runp', 'Downloaders.py', 'download_sfx:'+args]
        p = subprocess.Popen(cmd)
        utils.wait_timeout(p, config.FREESOUND_TIMEOUT)


def download_sfx(litter_id, key, download_path, download_num):
    logger.info('Downloading...')
    client = freesound.FreesoundClient()
    client.set_token(key)
    i = 0

    while i < download_num:
        try:
            response = client.get_sound(random.randint(0, 96451))
            url = response.url
            name = str(i) + '.mp3'
            response.retrieve_preview(download_path, name=name)
            store(litter_id, url, 'sfx')
            i += 1
        except Exception as e:
            logger.error('Exception occrured while downloading sfx...')
            logger.error(e)
