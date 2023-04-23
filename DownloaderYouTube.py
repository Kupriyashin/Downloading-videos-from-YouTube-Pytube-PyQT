import json

from pydantic import BaseModel

import pytube.exceptions
from loguru import logger
from pytube import YouTube
import backoff

"""
Информация по бибилиотеке Pytube - https://tehnojam.ru/category/development/pytube-skachivaem-youtube-video-s-pomoshju-python.html
Информация по бибилиотеке PyQT5 - https://python-scripts.com/pyqt5#install-pyqt5-designer
Информация по бибилиотеке backoff - https://backoff-utils.readthedocs.io/en/latest/using.html
"""


class information_video(BaseModel):
    description: str  # Описание видео
    keywords: str  # Ключевые слова видео
    publish_date: str  # Дата публикации видео
    rating: str  # Рейтинг видео
    thumbnail_url: str  # эскиз URL-адреса
    title: str  # Название видео
    author: str  # Автор видео


@logger.catch()
# здесь стоит декоратор потому-что получение атрибутов видео через класс YouTube срабтывает с 10% вероятностью (баг, или сам ютуб гадит)
@backoff.on_exception(backoff.expo,
                      exception=(pytube.exceptions.PytubeError, KeyError),
                      max_tries=5,
                      jitter=None
                      )
def downloader_video():

    _url_video = "https://youtu.be/8Zw-SUz3og8"
    _video_youtube = YouTube(url=_url_video)

    _information_video = {
        'description': str(_video_youtube.description),
        'keywords': str(_video_youtube.keywords),
        'publish_date': str(_video_youtube.publish_date),
        'rating': str(_video_youtube.rating),
        'thumbnail_url': str(_video_youtube.thumbnail_url),
        'title': str(_video_youtube.title),
        'author': str(_video_youtube.author)
    }

    _information_video = json.dumps(_information_video, ensure_ascii=False)
    _information_video = information_video.parse_raw(_information_video)

    logger.info(_information_video.title)


if __name__ == '__main__':
    downloader_video()
