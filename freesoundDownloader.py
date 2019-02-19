import random

import freesound
import requests

import config

HOST = 'www.freesound.org'
BASE = 'https://' + HOST + '/apiv2'

def get_sound_id(word):
    TEXT_SEARCH = '/search/text/'
    url = BASE + TEXT_SEARCH + '?query=' + word + '&token='+config.FREESOUND_API_KEY
    response = requests.get(url)

    print('response:', response.status_code)
    print('response:', response.reason)
    response = response.json()
    print(response.keys())

    result_count = len(response['results'])
    if result_count:
        index = random.randint(0, result_count-1)
        print(response['results'][index])
        print(response['results'][index]['name'])
        return response['results'][index]['id'], response['results'][index]['name']


def get_download_url(sound_id, sound_name):
    print('inside download_sound')



    name = sound_name.replace(' ', '_')

     # url = 'http://www.freesound.org/data/previews/' + str(sound_abrv) + '/' + str(name) + '.mp3'

    #/ apiv2 / sounds / < sound_id > /

    #'http://www.freesound.org/data/previews/187/187839_2-lq.mp3' #BASE + DOWNLOAD

    # headers = {'Authorization: Token': config.SFX_PATH}

    header = {''}
    url = BASE + '/sounds/' + str(sound_id) + '/' #'&token='+config.FREESOUND_API_KEY



    print('Download from...', url)
    #
    response = requests.get(url)
    print('response:', response.status_code)
    print('response:', response.reason)
    print('response:', response)


# id, name = get_sound_id('hi')
# get_download_url(id, name)
def download_sfx(litter_id, download_num):
    client = freesound.FreesoundClient()
    client.set_token(config.FREESOUND_API_KEY)
    i = 0

    while i < int(download_num):
        try:
            """
            TODO: Implement function to get sound id and build url
            response = client.get_sound(random.randint(0, 96451))
            """
            response = client.get_sound(random.randint(0, 96451))
            url = response.url
            name = str(i) + '.mp3'
            """
            TODO: call downloader 
            """
            response.retrieve_preview('./', name=name)
            # store(litter_id, url, 'sfx')
            i += 1
        except Exception as e:
            print(e)
            # logger.error('Exception occrured while downloading sfx...')
            # logger.error(e)

print('hello')
download_sfx(123, 1)
print('good bye')


