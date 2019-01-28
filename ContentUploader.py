import logging
import os
import subprocess
import time

import requests
from moviepy.video.VideoClip import ImageClip, ColorClip, TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

import config

logging.basicConfig(filename=config.LOG, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)


class ContentUploader(object):
    def __init__(self, name, result_path, id):
        self.url = None
        self.name = name
        self.result_path = result_path
        self.thumb_path = config.THUMB_PATH
        self.logo_path = config.LOGO_PATH
        self.secret_path = config.SECRET_PATH
        self.id = id
        self.tags = None
        self.weight = None

    def upload_content(self):
        logger.warning('Creating thumbnail...')
        self.create_thumbnail()
        time.sleep(3)
        logger.warning('Getting weight...')
        self.get_weight()
        logger.warning('Uploading...')
        self.upload()
        logger.warning('Storing...')
        self.store()

    def create_thumbnail(self):
        color = (255, 255, 255)
        size = (1280, 720)
        background = ColorClip(size, color)
        logo = ImageClip(self.logo_path) \
            .resize(width=400, height=200) \
            .set_pos(('center', 'center'))
        text = TextClip(txt=str(self.id), size=(500, 500)).set_position(
            ('center', 'bottom'))
        CompositeVideoClip([background, logo, text]).save_frame(self.thumb_path)

    def upload(self):
        logger.warning('attempting to upload file...')
        process_output = []
        category = 'Science & Technology'
        description = self.create_description()
        logger.warning('title: ' + self.name[:-4])
        logger.warning('description: ' + description)
        logger.warning('category: ' + category)
        logger.warning('tags: ' + self.tags)
        logger.warning('thumb_path: ' + self.thumb_path)
        logger.warning('results_path: ' + self.result_path)
        logger.warning('secret_path: ' + self.secret_path)
        upload_cmd = ['youtube-upload',
                      '--title=' + self.name[:-4],
                      '--description=' + description,
                      '--category=' + category,
                      '--tags=' + self.tags,
                      '--thumbnail=' + self.thumb_path,
                      '--client-secrets=' + self.secret_path,
                      self.result_path]
        try:
            proc = subprocess.Popen(upload_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in proc.stdout:
                entry = line.decode('utf-8')
                process_output.append(entry)
            proc.wait()
            self.url = self.extract_url(process_output)
            logger.warning('resulting url: ' + self.url)
        except subprocess.CalledProcessError as e:
            logger.error('Error called in ContentUploader.upload()')
            logger.error(e)

    @staticmethod
    def extract_url(process_output):
        logger.warning('extracting url...')
        yt_url_base = 'https://www.youtube.com/watch?v='
        key = "Video URL:"
        for entry in process_output:
            logger.warning('searching entry: ' + entry)
            if key in entry:
                logger.warning('key found!!!')
                url_start_index = entry.find(yt_url_base)
                if url_start_index != -1:
                    logging.warning('url_start_index: ' + str(url_start_index))
                    url_end_index = url_start_index + len(yt_url_base) + 11
                    return entry[url_start_index: url_end_index]
        return ""

    def create_description(self):
        return 'Content ID ' + str(self.id) + ' was generated by the LitterBug script in an ' \
                                              'attempt to raise environmental awareness online.\n\n' \
                                              'To learn more about Project Litter Bug, please ' \
                                              'visit http://projectlitterbug.com\n\n' \
                                              'The full source code for this project can be ' \
                                              'found at ' \
                                              'https://github.com/nkelton/Project-Litter-Bug\n\n\n' \
                                              'CONTENT STATS...\n\n\n' \
                                              'Weight: ' + str(self.weight) + ' Bytes\n\n' \
               + self.retrieve_content_lst()

    def retrieve_content_lst(self):
        url = self._url('/content/' + str(self.id) + '/')
        response = requests.get(url)
        if response.status_code == 200:
            temp = response.json()
            vid_str = self.create_content_str(temp, 'vid')
            gif_str = self.create_content_str(temp, 'gif')
            pic_str = self.create_content_str(temp, 'pic')
            sfx_str = self.create_content_str(temp, 'sfx')
            return 'Videos used:' + vid_str + 'Gifs used:' + gif_str + \
                   'Pictures used:' + pic_str + 'Sfx used:' + sfx_str
        else:
            return 'Content stats currently unavailable...'

    @staticmethod
    def create_content_str(data, media):
        content_str = '\n'
        for d in data:
            if d['type'] == media:
                content_str += d['url'] + '\n'
        return content_str

    def get_weight(self):
        if os.path.exists(self.result_path):
            logger.error('weight exists!')
            self.weight = os.path.getsize(self.result_path)
        else:
            self.weight = 0

    def store(self):
        url = self._url('/litter/')
        logger.error('POST to url: ' + url + ' %%%%')
        logger.error('litter_id: ' + str(self.id))
        logger.error('name: ' + self.name[:-4])
        logger.error('url: ' + self.url + ' %%%%')
        logger.error('weight: ' + str(self.weight))
        response = requests.post(url, json={
            'litter_id': self.id,
            'title': self.name[:-4],
            'url': self.url,
            'weight': self.weight,
        })
        logger.error('POST RESPONSE: ' + response.text)

    @staticmethod
    def _url(path):
        return config.BASE_URL + path

    def set_tags(self, tags):
        self.tags = tags
