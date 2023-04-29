from __future__ import annotations

import time
import traceback

from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5 import QtWidgets
from Form_download import Ui_MainWindow
import sys
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QRegExp

from loguru import logger
from pytube import YouTube

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

        self.ui.lineEdit_2.setStyleSheet("""QLineEdit { background-color: rgb(255, 0, 0, 0.06);}""")
        self.ui.listWidget.setStyleSheet(
            "QListWidget{background: rgb(240,240,240);border : 2px solid rgb(240,240,240)}")
        self.ui.lineEdit.setValidator(
            QRegExpValidator(QRegExp(r"^(http(s)?:\/\/)?((w){3}.)?youtu(be|.be)?(\.com)?\/.+")))

        self.ui.pushButton_2.clicked.connect(self.button_directory)
        self.ui.pushButton.clicked.connect(self.button_download_stream)

    def list_add_item(self, text: str, true_false: bool):
        try:

            if true_false:
                self.ui.listWidget.addItem(f"✅{datetime.now().strftime('%H:%M:%S')} - {text}")
                self.ui.listWidget.scrollToBottom()

            else:
                self.ui.listWidget.addItem(f"❌{datetime.now().strftime('%H:%M:%S')} - {text}")
                self.ui.listWidget.scrollToBottom()

        except Exception:

            self.ui.listWidget.addItem(
                f"❌{datetime.now().strftime('%H:%M:%S')} - Произошла внутренняя ошибка обмена данными")
            self.ui.listWidget.addItem(
                f"❌{datetime.now().strftime('%H:%M:%S')} - ❌ПЕРЕЗАГРУЗИТЕ ПРИЛОЖЕНИЕ!❌")
            self.ui.listWidget.scrollToBottom()

    def button_download_stream(self):
        try:

            if self.ui.lineEdit.text():
                try:

                    pass

                except Exception:
                    logger.error(traceback.format_exc())
                    self.list_add_item(text='Произошла ошибка при загрузке форматов видео. Попробуйте еще раз!',
                                       true_false=False)
            else:
                logger.error(traceback.format_exc())
                self.list_add_item(text='Неверно указана ссылка на видео с Youtube',
                                   true_false=False)

        except Exception:
            logger.error(traceback.format_exc())
            self.list_add_item(text='Неверно указана ссылка на видео с Youtube',
                               true_false=False)

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

                self.list_add_item(text='Папка загрузки установлена',
                                   true_false=True)
            else:
                self.list_add_item(text='Произошла ошибка при выборе директории!',
                                   true_false=False)
        except Exception:
            self.list_add_item(text='Произошла ошибка при выборе директории!',
                               true_false=False)


class DownloadYoutube(QObject):
    signal_for_progressbar = pyqtSignal(int)  # для прогресс бара
    signal_process_false = pyqtSignal(str)  # сигнал для записи в listwidget неудачных попыток
    signal_stop_thread = pyqtSignal()  # сигнал, который испускается если вся работа выполнена
    signal_finish = pyqtSignal(list)  # сигнал для передачи полученных данных

    def __init__(self, url_video: str):
        super(DownloadYoutube, self).__init__()
        self.url = url_video

    @logger.catch()
    def video_streams(self):
        _streams = []
        for _ in range(10):



"""
Здесь один из вариантов того, как можно еще раз вызвать функцию если она выкатила ошибку.
Но я так подумал и решил реализовать через цикл (особенно если используются потоки)

    # @logger.catch()
    # # здесь стоит декоратор потому-что получение атрибутов видео через класс YouTube срабатывает с 10% вероятностью (баг или сам ютуб гадит)
    # @backoff.on_exception(backoff.expo,
    #                       exception=(pytube.exceptions.PytubeError, KeyError),
    #                       max_time=20,
    #                       max_tries=5,
    #                       jitter=None,
    #                       logger=logger
    #                       )
    # # тута получаем стримы для скачивания контента (шо такое стримы в данной бибилиотеке - читайте в документации библиотеки)
    # def video_streams(self):
    #     self.signal_work.emit(f"{datetime.now().strftime('%H:%M:%S')} - Пытаюсь найти видео")
    # 
    #     video_youtube = YouTube(url=self.url)
    #     self.streams = list(enumerate(video_youtube.streams.all()))
    #     logger.info(self.streams)
    # 
    #     self.signal_finish.emit(self.streams)
"""

"""
Самое фиговое в backoff то, что если поставить try except, backoff не будет работать. 
Соответственно, было принято  решение, если по истечению времени ничего не подключилось, 
ловить ошибку об этом в потоке и потом закидывать в ListWidget
"""

#     try:
#         # self.signal_for_progressbar.emit(int(_ * 100 / 10))
#         #
#         # _video_youtube = YouTube(url=self.url)
#         #
#         # _streams = list(enumerate(_video_youtube.streams.all()))
#         # logger.info(_streams)
#         #
#         # # if _streams:
#         # #     self.signal_finish.emit(_streams)
#         # #     self.signal_stop_thread.emit()
#         # #     break
#         # #
#         # # else:
#         # #     self.signal_process_false.emit("Ответа не последовало! Попробуйте еще раз указать ссылку.")
#
#     except Exception as error:
#         self.signal_process_false.emit("Неудачная попытка")
#         logger.info("ОШибка с видосом!", error=error)
#         time.sleep(3)
# # self.signal_stop_thread.emit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Programm_Window()
    ex.show()
    app.exec_()
