with open('requiremеnts.txt', 'r') as requiremеnts:
    tokenVK = requiremеnts.readline()
    # tokenYD = requiremеnts.readline()

import requests
from pprint import pprint
import json
import logging

logging.basicConfig(
    level=logging.DEBUG,
    filename = "mylog.log",
    format = "%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S',
    )
logging.info('Hello')

def VKphotos_search(owner_id, number_photos=5):
    VKphotos_search_url = 'https://api.vk.com/method/photos.get'
    VKphotos_search_params = {
        'access_token': tokenVK,
        'v': '5.131',
        'owner_id': owner_id,
        'album_id': 'profile',
        'extended': 1,
        'photo_sizes': 1
    }
    req = requests.get(VKphotos_search_url, VKphotos_search_params).json()
    photos_list = []
    counter = 0
    for i in req['response']['items']:
        if counter < number_photos:
            photo_dict = {}
            size_max = 0
            photo_likes = i['likes']['count']
            for photo in i['sizes']:
                if photo['width'] * photo['height'] >= size_max:
                    size_max = photo['width'] * photo['height']
                    photo_type = photo['type']
                    photo_url = photo['url']
            photo_dict['file_name'] = f'{photo_likes}.jpg'
            photo_dict['size'] = photo_type
            photo_dict['photo_url'] = photo_url
            photos_list.append(photo_dict)
            counter += 1
        else:
            break
    return photos_list

def recordingYD(owner_id, tokenYD):
    upload_url_put = 'https://cloud-api.yandex.net/v1/disk/resources'
    headers = {
        'Content-Type': 'application/json', 
        'Authorization': 'OAuth {}'.format(tokenYD)
    }
    params_folder_creation = {'path': owner_id}
    folder_creation = requests.put(upload_url_put, headers=headers, params=params_folder_creation).json()

    upload_url_upload = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    for photo in VKphotos_search(owner_id, number_photos=5):
        params_recording = {
            'path': f'{owner_id}/{photo["file_name"]}', 
            'url': photo['photo_url']
        }
        recording = requests.post(upload_url_upload, headers=headers, params=params_recording).json()
    file_information = VKphotos_search(owner_id, number_photos=5)
    for file in file_information:
        file.pop('photo_url')
    with open('file_information.txt', 'a') as out_file:
        json.dump(file_information, out_file)
    return file_information
    

if __name__ == '__main__':    
    owner_id = input('Введите номер id пользователя VK: ')
    tokenYD = input('Введите токен с Полигона Яндекс.Диска: ')
    pprint(recordingYD(owner_id, tokenYD))