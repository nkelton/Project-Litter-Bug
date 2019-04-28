import logging
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ''

YOUTUBE_API_KEY = ''
GIPHY_API_KEY = ''
PIXABAY_API_KEY = ''
FREESOUND_API_KEY = ''

AUTH = ('', '')

BASE_PATH = os.path.expanduser('')

VID_PATH = BASE_PATH + 'media/video/'
GIF_PATH = BASE_PATH + 'media/gif/'
PIC_PATH = BASE_PATH + 'media/pic/'
SFX_PATH = BASE_PATH + 'media/sfx/'
LOGO_PATH = BASE_PATH + 'media/intro/logo.jpg'
RESULT_PATH = BASE_PATH + 'media/result/'
THUMB_PATH = BASE_PATH + 'media/thumbnail/thumb.png'
SECRET_PATH = BASE_PATH + 'secret/client_secret.json'

BASE_URL = 'http://127.0.0.1:8000'

DOWNLOAD_TIMEOUT = 120

CREATE_TIMEOUT = 14400
CREATE_INTERVAL = 900

LITTER_BUG_TIMEOUT = 14400
LITTER_BUG_INTERVAL = 600

TIMEOUT_DOWNLOAD_TRACKER = 0
GLOBAL_DOWNLOAD_TRACKER = 0

LOG = 'plb.log'

YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the {{ Cloud Console }}
{{ https://cloud.google.com/console }}

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   SECRET_PATH))


def set_logger(module):
    logging.basicConfig(filename=LOG, format='%(asctime)s %(levelname)-8s %(name)-15s %(message)s',
                        level=logging.DEBUG)
    return logging.getLogger(module)
