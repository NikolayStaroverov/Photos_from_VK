import requests
import datetime
import os
from tqdm import tqdm


class VKAPIClient:
        API_BASE_url = 'https://api.vk.com/method/'

        def __init__(self, token, user_id):
                self.token = token
                self.user_id = user_id

        def get_common_params(self):
                return {'access_token': self.token, 'v': '5.150', 'owner_id': self.user_id, 'album_id': 'wall', 'extended': 1}

        def _build_url(self, apimethod):
                return f'{self.API_BASE_url}/{apimethod}'

        def get_photos(self):
                params = self.get_common_params()
                response = requests.get(self._build_url('photos.get'), params=params)
                photos_data = response.json()['response']
                number_of_photos = photos_data['count']
                if not os.path.exists('Photos from VK'):
                        os.mkdir('Photos from VK')
                os.chdir(str(os.getcwd()) + str("\Photos from VK"))
                photos_list = []
                # создание списка словарей фотографий и их URL
                for i in tqdm(range(number_of_photos), desc='Сохранение файлов с VK на компьютер'):
                        best_height = 0
                        # поиск фото с максимальным разрешением
                        for n in range(len(photos_data['items'][i]['sizes'])):
                                if photos_data['items'][i]['sizes'][n].get('height') > best_height:
                                        best_height = photos_data['items'][i]['sizes'][n].get('height')
                                        type_of_photo = photos_data['items'][i]['sizes'][n].get('type')
                                        photo_url = photos_data['items'][i]['sizes'][n]['url']
                        # количество лайков
                        number_of_likes = photos_data['items'][i]['likes']['count']
                        # Дата в формате Unixtime
                        date_Unixtime = photos_data['items'][i]['date']
                        date_time_split = []
                        date_time_split = str(datetime.datetime.fromtimestamp(date_Unixtime)).split(' ')
                        # все фото загружены в один день и в этом случае сохранится только одна фотография с датой этого дня
                        # поэтому дополнительно в названии файла указывается время
                        date_split = str(date_time_split[0]).split('-')
                        time_split = str(date_time_split[1]).split(':')
                        date_time_readble = '_'.join(date_split)+'_ '+'_'.join(time_split)
                        name_of_photo = "_".join([date_time_readble, str(number_of_likes)])+'.jpg'

                        # список лчуших фото с их типами размера
                        photos_list.append({'file_name': name_of_photo, 'size': type_of_photo})
                        # Сохранение фотографий на компьютер
                        with open(name_of_photo, 'wb') as file:
                                file.write(requests.get(photo_url).content)
                return photos_list

        def save_to_YD(self, photos_list):
                tok_YD = input("Введите Ваш токен Яндекс:")
                token_YD = "OAuth "+tok_YD
                base_url = "https://cloud-api.yandex.net"
                headers = {"Authorization": token_YD}
                url_for_new_folder = base_url+"/v1/disk/resources"
                Folder_name = input("Введите название папки на Яндекс Диске:")
                params = {'path': Folder_name}

                # Создание новой папки
                response = requests.put(url_for_new_folder, headers=headers, params=params)

                # Запросить url для загрузки
                url_for_get_link = url_for_new_folder+"/upload"

                # Запись файлов на Яндекс Диск
                for i in tqdm(range(len(photos_list)), desc='Запись файлов на Яндекс Диск'):
                        params = {'path': Folder_name+'/'+photos_list[i].get('file_name')}
                        response = requests.get(url_for_get_link, params=params, headers=headers)
                        url_upload = response.json().get('href', '')
                        with open(photos_list[i].get('file_name'), 'rb') as file:
                                response = requests.put(url_upload, files={"file": file})


if __name__ == '__main__':
        TOKEN = input("Введите токен VK:")
        ID_VK = input("Введите Ваш ID VK:")
        vk_client = VKAPIClient(TOKEN, ID_VK)
        photos_list = vk_client.get_photos()
        photos_save = vk_client.save_to_YD(photos_list)