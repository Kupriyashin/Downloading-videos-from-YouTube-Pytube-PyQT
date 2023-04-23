from pprint import pprint

import pytube.exceptions
from loguru import logger
from pytube import YouTube
import backoff

"""
Информация по бибилиотеке Pytube - https://tehnojam.ru/category/development/pytube-skachivaem-youtube-video-s-pomoshju-python.html
Информация по бибилиотеке PyQT5 - https://python-scripts.com/pyqt5#install-pyqt5-designer
"""


# pytube.exceptions.PytubeError

@logger.catch()
# здесь стоит декоратор потому-что получение атрибутов видео через класс YouTube срабтывает с 10% вероятностью (баг, или сам ютуб гадит)
@backoff.on_exception(backoff.expo,
                      exception=(pytube.exceptions.PytubeError, KeyError),
                      max_tries=10,
                      jitter=None
                      )
def downloader_video():
    url_video = "https://youtu.be/C2aceW7_4lE"
    video_youtube = YouTube(url=url_video)
    print(video_youtube.title)


if __name__ == '__main__':
    downloader_video()
