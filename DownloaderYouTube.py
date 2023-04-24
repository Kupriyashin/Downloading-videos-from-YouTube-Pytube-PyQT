import json
import random
from pprint import pprint

import pytube.exceptions
from loguru import logger
from pytube import YouTube
import backoff

"""
Информация по бибилиотеке Pytube - https://tehnojam.ru/category/development/pytube-skachivaem-youtube-video-s-pomoshju-python.html
Информация по бибилиотеке PyQT5 - https://python-scripts.com/pyqt5#install-pyqt5-designer
Информация по бибилиотеке backoff - https://backoff-utils.readthedocs.io/en/latest/using.html
"""


class DownloadYoutube:
    def __init__(self, url_video: str):
        self.streams = None
        self.video_youtube = YouTube(url=url_video)

    @logger.catch()
    # здесь стоит декоратор потому-что получение атрибутов видео через класс YouTube срабатывает с 10% вероятностью (баг или сам ютуб гадит)
    @backoff.on_exception(backoff.expo,
                          exception=(pytube.exceptions.PytubeError, KeyError),
                          max_tries=10,
                          jitter=None,
                          logger=logger
                          )
    # тута получаем стримы для скачивания контента (шо такое стримы в данной бибилиотеке - читайте в документации библиотеки)
    def video_streams(self) -> list:
        self.streams = list(enumerate(self.video_youtube.streams.all()))
        logger.info(self.streams)

        return self.streams


if __name__ == '__main__':
    downloader = DownloadYoutube(url_video="https://www.youtube.com/watch?v=-pDSFQSB5Ac")
    print(downloader.video_streams())
