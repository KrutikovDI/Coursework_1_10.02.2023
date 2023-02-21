# Читаем файл с токенами и сохраняем в переменные
import configparser
config = configparser.ConfigParser()  # создаём объекта парсера
config.read("token.ini")  # читаем конфиг
tokenVK = config['token']['tokenVK']
tokenYD = config['token']['tokenYD']

import requests
from pprint import pprint
import json
import logging

# Создам логирование для отслеживания процесса программы, сохраняем в файл 'mylog.log'
logging.basicConfig(
    level=logging.DEBUG,
    filename = "mylog.log",
    format = "%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S',
    )
logging.info('Hello')

# Создаем класс для работы с API Вконтакте и добавляем классу несколько атрибутов: url и общие параметры 
class VKUser:
    url = 'https://api.vk.com/method/'
    def __init__(self, tokenVK, version):
        self.params = {'access_token': tokenVK,
                       'v': version
                      }
# Создаем функцию нашего класса для сохранения фотографий пользователя Вконтакте в список photos_list
    def VKphotos_search(self, user_ids, number_photos):
        VKuser_ids_url = self.url + 'users.get'
        VKuser_ids_params = {
            'user_ids': user_ids,
        }
        req = requests.get(VKuser_ids_url, params={**self.params, **VKuser_ids_params}).json()
        owner_id = req['response'][0]['id'] # если пользователь вводит screen_name пользователя, у котого необходимо сохранить фото, вместо его id, программа получает корректный id для дальнейшей работы
        VKphotos_search_url = self.url + 'photos.get'
        VKphotos_search_params = {
            'owner_id': owner_id,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1
        }
        req = requests.get(VKphotos_search_url, params={**self.params, **VKphotos_search_params}).json() # по id получаем файл json, содержащий всю информацию о фотографиях, которая нам необходима для дальнейшей работы. Все нужные характеристики прописываем в параметрах
        photos_list = []
        name_list = []
        counter = 0
        for i in req['response']['items']: # сохраним необходимое количество фотографий в список photos_list, указав нужные характеристики. Количество фотографий будем зарпашивать у пользователя при вызове функции
            if counter < number_photos:
                photo_dict = {}
                size_max = 0
                photo_likes = i['likes']['count']
                photo_date = i['date']
                for photo in i['sizes']:
                    if photo['width'] * photo['height'] >= size_max: # Сохранияе в photos_list  только фотографии максимального размера
                        size_max = photo['width'] * photo['height']
                        photo_type = photo['type']
                        photo_url = photo['url']
                if photo_likes not in name_list: # Название фотограциям присваиваем по количетсву лайков. Если количество лайков у фото равно, тогда к названию добавляется дата.
                    photo_dict['file_name'] = f'{photo_likes}.jpg'
                else:
                    photo_dict['file_name'] = f'{photo_likes}{photo_date}.jpg'
                name_list.append(photo_likes)
                photo_dict['size'] = photo_type
                photo_dict['photo_url'] = photo_url
                photos_list.append(photo_dict) 
                counter += 1
            else:
                break
        return photos_list

# Создаем класс для рабты с Яндекс диском, добавляем классу несколько атрибутов: общие url и заголовки headers 
class YDisk:
    url = 'https://cloud-api.yandex.net/v1/disk/'
    def __init__(self, tokenYD):
        self.headers = {
            'Content-Type': 'application/json', 
            'Authorization': 'OAuth {}'.format(tokenYD)
        }
# Создаем функцию для нашего класса, которая записывает фотографии на Яндекс диск и сохраняет json-файл с информацией по файлу в file_information.txt
    def recordingYD(self, name_folder, photos_list):
        upload_url_put = self.url + 'resources'
        params_folder_creation = {'path': name_folder}
        folder_creation = requests.put(upload_url_put, headers=self.headers, params=params_folder_creation).json() # создаем папку на Яндекс диске, куда будем сохранять полученные фотографии. Папку называем введеным имененм пользоватееля
    
        upload_url_upload = self.url + 'resources/upload'
        for photo in photos_list:
            params_recording = {
                'path': f'{name_folder}/{photo["file_name"]}', 
                'url': photo['photo_url']
            }
            recording = requests.post(upload_url_upload, headers=self.headers, params=params_recording).json() # в созданную папку на Яндекс диске сохраняем полученные фотографии

# сохраним json-файл с информацией по файлу в file_information.txt, предварительно удаляя из изфайла url-фото (требование ТЗ)
        file_information = photos_list
        for file in file_information:
            file.pop('photo_url')
        with open('file_information.txt', 'a') as out_file:
            json.dump(file_information, out_file)
        
        return file_information
    

if __name__ == '__main__':    
    vk_photos = VKUser(tokenVK, '5.131')
    yd_photos = YDisk(tokenYD)
    user_ids = input('Введите номер id или screen_name пользователя VK: ')
    number_photos = int(input('Введите количество загружаемых фото: '))
    pprint(yd_photos.recordingYD(user_ids, vk_photos.VKphotos_search(user_ids, number_photos)))