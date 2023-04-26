from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5 import QtWidgets
from Form_download import Ui_MainWindow
import sys
from datetime import datetime

import pytube.exceptions
from loguru import logger
from pytube import YouTube
import backoff

"""
Информация по бибилиотеке Pytube - https://pytube3.readthedocs.io/en/latest/user/quickstart.html
Информация по бибилиотеке PyQT5 - https://python-scripts.com/pyqt5#install-pyqt5-designer
Информация по бибилиотеке backoff - https://backoff-utils.readthedocs.io/en/latest/using.html
"""
logger.add("debug.log", format="{time} {level} {message}", level="DEBUG")


class Programm_Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Programm_Window, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.lineEdit.setEnabled(False)
        self.ui.pushButton.setEnabled(False)
        self.ui.comboBox.setEnabled(False)
        self.ui.pushButton_3.setEnabled(False)

        self.ui.lineEdit_2.setStyleSheet("""
        QLineEdit { 
        background-color: rgb(255, 0, 0, 0.06);
        }
        """)
        self.ui.pushButton_2.clicked.connect(self.button_directory)
        self.ui.pushButton.clicked.connect(self.button_download_stream)

    def button_download_stream(self):
        try:
            if self.ui.lineEdit.text():
                try:
                    _streams = DownloadYoutube(url_video=self.ui.lineEdit.text()).video_streams(self)

                    if _streams:
                        print(_streams)

                    else:
                        self.ui.listWidget.addItem(
                            f"{datetime.now().strftime('%H:%M:%S')} - Произошла ошибка при загрузке форматов видео. Попробуйте еще раз!")

                except Exception:

                    self.ui.listWidget.addItem(
                        f"{datetime.now().strftime('%H:%M:%S')} - Произошла ошибка при загрузке форматов видео. Попробуйте еще раз!")
            else:

                self.ui.listWidget.addItem(f"{datetime.now().strftime('%H:%M:%S')} - Неверно указана ссылка на видео с Youtube")

        except Exception:
            self.ui.listWidget.addItem(f"{datetime.now().strftime('%H:%M:%S')} - Неверно указана ссылка на видео с Youtube")

    def button_directory(self):
        try:
            _path_directory = QFileDialog.getExistingDirectory(self, 'Выберите папку для сохранения видеозаписи.')
            if _path_directory:

                self.ui.lineEdit_2.setText(f"{_path_directory}")

                self.ui.pushButton_2.setEnabled(False)
                self.ui.pushButton.setEnabled(True)
                self.ui.lineEdit.setEnabled(True)

                self.ui.lineEdit_2.setCursorPosition(0)
                self.ui.lineEdit_2.setStyleSheet("""
                        QLineEdit { 
                        background-color: rgb(255, 255, 255);
                        }
                        """)

                self.ui.lineEdit.setStyleSheet("""
                        QLineEdit { 
                        background-color: rgb(255, 0, 0, 0.06);
                        }
                        """)
            else:
                self.ui.listWidget.addItem(f"{datetime.now()} - Произошла ошибка при выборе директории!")

        except Exception:
            self.ui.listWidget.addItem(f"{datetime.now()} - Произошла ошибка при выборе директории!")


class DownloadYoutube():
    def __init__(self, url_video: str):
        self.streams = None
        self.video_youtube = YouTube(url=url_video)

    @logger.catch()
    # здесь стоит декоратор потому-что получение атрибутов видео через класс YouTube срабатывает с 10% вероятностью (баг или сам ютуб гадит)
    @backoff.on_exception(backoff.expo,
                          exception=(pytube.exceptions.PytubeError, KeyError),
                          max_time=20,
                          max_tries=5,
                          jitter=None,
                          logger=logger
                          )
    # тута получаем стримы для скачивания контента (шо такое стримы в данной бибилиотеке - читайте в документации библиотеки)
    def video_streams(self, qt_class) -> list:
        qt_class.ui.listWidget.addItem(f"{datetime.now().strftime('%H:%M:%S')} - Пытаюсь найти видео")

        self.streams = list(enumerate(self.video_youtube.streams.all()))
        logger.info(self.streams)

        return self.streams


"""
Самое фиговое в backoff то, что если поставить try except, backoff не будет работать. 
Соответственно, было принято  решение, если по истечению времени ничего не подключилось, 
ловить ошибку об этом в потоке и потом закидывать в ListWidget
"""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Programm_Window()
    ex.show()
    app.exec_()
