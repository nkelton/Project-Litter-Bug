import os
import subprocess
import sys

import httplib2
import requests
from apiclient.discovery import build
from googleapiclient.errors import HttpError
from moviepy.video.VideoClip import ImageClip, ColorClip, TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

import config

logger = config.set_logger('ContentUploader.py')


class ContentUploader(object):
    def __init__(self, name, result_path, id):
        self.url = None
        self.name = name
        self.result_path = result_path
        self.id = id
        self.tags = None
        self.weight = None

    def upload_content(self):
        logger.info('Uploading content...')
        self.get_weight()
        self.upload()
        self.store()
        self.create_thumbnail()
        self.set_thumbnail()

    def upload(self):
        logger.info('Uploading...')
        category = 'Science & Technology'
        description = self.create_description()
        process_output = []

        upload_cmd = ['youtube-upload',
                      '--title=' + self.name[:-4],
                      '--description=' + description,
                      '--category=' + category,
                      '--tags=' + self.tags,
                      '--client-secrets=' + config.SECRET_PATH,
                      self.result_path]

        try:
            logger.info('Attempting to run youtube-upload...')
            proc = subprocess.Popen(upload_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in proc.stdout:
                entry = line.decode('utf-8')
                logger.info('appending entry:' + entry)
                process_output.append(entry)
            proc.wait()
            self.url = self.extract_url(process_output)
            logger.info('resulting url: ' + self.url)

        except subprocess.CalledProcessError as e:
            logger.error('Error occured while attempting to run youtube-upload')
            logger.error(e)

    @staticmethod
    def extract_url(process_output):
        logger.info('Extracting url...')
        yt_url_base = 'https://www.youtube.com/watch?v='
        key = "Video URL:"
        for entry in process_output:
            if key in entry:
                logger.info('Key found!')
                url_start_index = entry.find(yt_url_base)
                if url_start_index != -1:
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
        logger.info('Getting weight...')
        if os.path.exists(self.result_path):
            logger.error('Weighing result...')
            self.weight = os.path.getsize(self.result_path)
        else:
            self.weight = 0

    def store(self):
        logger.info('Storing data...')
        url = self._url('/litter/')
        requests.post(url, json={
            'litter_id': self.id,
            'title': self.name[:-4],
            'url': self.url,
            'weight': self.weight,
        })

    def create_thumbnail(self):
        logger.info('Creating thumbnail...')
        color = (255, 255, 255)
        size = (1280, 720)
        background = ColorClip(size, color)
        logo = ImageClip(config.LOGO_PATH) \
            .resize(width=400, height=200) \
            .set_pos(('center', 'center'))
        text = TextClip(txt=str(self.id), size=(500, 500)).set_position(
            ('center', 'bottom'))
        CompositeVideoClip([background, logo, text]).save_frame(config.THUMB_PATH)

    def set_thumbnail(self):
        logger.info('Setting thumbnail...')

        def get_authenticated_service():
            logger.info('Authenticating servie...')
            flow = flow_from_clientsecrets(config.SECRET_PATH,
                                           scope=config.YOUTUBE_READ_WRITE_SCOPE,
                                           message=config.MISSING_CLIENT_SECRETS_MESSAGE)

            storage = Storage("%s-oauth2.json" % sys.argv[0])
            credentials = storage.get()

            if credentials is None or credentials.invalid:
                credentials = run_flow(flow, storage)

            return build(config.YOUTUBE_API_SERVICE_NAME, config.YOUTUBE_API_VERSION,
                         http=credentials.authorize(httplib2.Http()))

        def upload_thumbnail(youtube, video_id):
            logger.info('Uploading thumbnail...')
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=config.THUMB_PATH
            ).execute()

        youtube = get_authenticated_service()
        logger.info('Attaching thumbnail to videoId: ' + self.url[-11:])
        try:
            upload_thumbnail(youtube, self.url[-11:])
        except HttpError as e:
            logger.error("Error occured setting thumbnail...")
            logger.error(e.content)
        else:
            logger.info("Thumbnail successfully set.")

    @staticmethod
    def _url(path):
        return config.BASE_URL + path

    def set_tags(self, tags):
        self.tags = tags
