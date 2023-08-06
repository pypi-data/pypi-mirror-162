import binascii
import logging
import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter


class SpiderWai77:

    def __init__(self, girl_name, file_path):
        requests.session().mount('https//', HTTPAdapter(max_retries=3))
        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        logging.basicConfig(level=logging.INFO, format=log_format)
        self.__headers = {
            'User-Agent': UserAgent().random,
            'Connection': 'close'
        }
        self.__girl_id = ''
        self.__girl_name = girl_name
        self.__girl_path = ''
        self.__file_path = file_path
        self.__album_ids = []
        self.__album_num = 0
        self.__init_members()
        index = 0
        while True:
            self.__album_num = len(self.__album_ids)
            if self.__album_num == 0:
                break
            logging.info(f'{index} execution starts {self.__album_num} albums')
            self.__execute()
            logging.info(f'{index} execution completed {self.__album_num - len(self.__album_ids)} albums')
            index += 1
        logging.info('verify starts')
        self.__verify()
        logging.info('verify ends')

    def __init_members(self):
        cover_links = []
        page = 1
        while True:
            res = requests.get(f'https://www.wai77.com/category/{self.__girl_name}/page/{page}', headers=self.__headers, timeout=10)
            if res.status_code != 200:
                break
            cover_links.extend([cover_link['src'] for cover_link in BeautifulSoup(res.text, 'lxml').find_all(class_='attachment-post-thumbnail size-post-thumbnail wp-post-image')])
            page += 1

        self.__girl_id = re.search(r'/gallery/([A-Za-z0-9]+)/', cover_links[0]).group(1)
        self.__girl_path = f'{self.__file_path}\\{self.__girl_id}'
        if not os.path.exists(self.__girl_path):
            os.mkdir(self.__girl_path)
        self.__album_ids = [re.search(r'/([A-Za-z0-9]+)/cover/', cover_link).group(1) for cover_link in cover_links]

    def __execute(self):

        # 字符串修正，pattern = 0 修正为文件名，pattern = 1 修正为链接名
        def str_fix(n, pattern):
            if n == '0':
                if pattern == 0:
                    return '000'
                elif pattern == 1:
                    return '0'
            elif len(n) == 1:
                return '00' + n
            elif len(n) == 2:
                return '0' + n
            elif len(n) == 3:
                return n

        def run(index):
            thread_name = threading.current_thread().name
            logging.info(f'{thread_name} starts')
            album_id = self.__album_ids[index]
            folder_path = f'{self.__girl_path}\\{album_id}'
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)
            page = 0
            while True:
                true_url = f'https://www.wai77.com/gallery/{self.__girl_id}/{album_id}/{str_fix(str(page), 1)}.webp'
                res = requests.get(true_url, headers=self.__headers, timeout=10)
                if res.status_code != 200:
                    break
                with open(f'{folder_path}\\{str_fix(str(page), 0)}.webp', 'wb') as f:
                    f.write(res.content)
                page += 1
            del self.__album_ids[index]
            logging.info(f'{thread_name} ends')

        with ThreadPoolExecutor(self.__album_num) as tpe:
            for i in range(self.__album_num):
                tpe.submit(run, index=i)

    def __verify(self):
        for album_id in os.listdir(self.__girl_path):
            folder_path = f'{self.__girl_path}\\{album_id}'
            if os.path.isdir(folder_path):
                for name in os.listdir(f'{self.__girl_path}\\{album_id}'):
                    img_path = f'{self.__girl_path}\\{album_id}\\{name}'
                    with open(img_path, 'rb') as f:
                        all_data = f.readlines()
                        if len(all_data) == 0 or not binascii.b2a_hex(all_data[-1]).decode('unicode_escape').endswith('00'):
                            true_url = f'https://www.wai77.com/gallery/{self.__girl_id}/{album_id}/{name}'
                            with open(img_path, 'wb') as w:
                                w.write(requests.get(true_url, headers=self.__headers).content)
                            logging.info(f'{img_path} fixed')
