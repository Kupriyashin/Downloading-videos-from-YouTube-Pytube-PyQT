from __future__ import annotations

import time
import traceback
from typing import Optional

from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5 import QtWidgets, QtCore
from Form_download import Ui_MainWindow
import sys
from datetime import datetime
from PyQt5.QtCore import pyqtSignal, QThread, QRegExp
from PyQt5.QtCore import Qt

from loguru import logger
from pytube import YouTube

"""
Информация по бибилиотеке Pytube - https://pytube3.readthedocs.io/en/latest/user/quickstart.html
Информация по бибилиотеке PyQT5 - https://python-scripts.com/pyqt5#install-pyqt5-designer
Информация по бибилиотеке backoff - https://backoff-utils.readthedocs.io/en/latest/using.html
Книга по PyQT5 - Python 3 и PyQt 5. Разработка приложений. — 2-е изд., перераб. и доп. / 
Н. А. Прохоренок, В. А. Дронов. — СПб.: БХВ-Петербург, 2018. — 832 с.: ил. —
(Профессиональное программирование)
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

    def progress_bar(self, in_put: int):
        self.ui.progressBar.setValue(in_put)

    def check_streams(self, streams_data):
        logger.info(str(streams_data))
        if streams_data:
            self.ui.pushButton.setEnabled(False)
            self.list_add_item(text="Обработка закончена, данные о видео получены!", true_false=True)
            self.ui.progressBar.setValue(100)
            self.ui.lineEdit.setEnabled(False)
        else:
            self.ui.pushButton.setEnabled(True)
            self.list_add_item(text="Обработка закончилась неудачей! ПОВТОРИТЕ ПОПЫТКУ", true_false=False)


    def button_download_stream(self):
        try:

            if self.ui.lineEdit.text():
                try:

                    # создаем экземпляр класса потока
                    self.streams_video_give = streams_video_give_multithreads(url_video=self.ui.lineEdit.text())

                    # в listwidget добавляется текст если запустилось в другом потоке
                    self.streams_video_give.started.connect(
                        lambda: self.list_add_item(text="Пытаюсь получить данные о видео", true_false=True))
                    # блокируется кнопка если запустилось в другом потоке
                    self.streams_video_give.started.connect(
                        lambda: self.ui.pushButton.setEnabled(False))

                    # заполняется прогресс бар
                    self.streams_video_give.signal_for_progressbar.connect(self.progress_bar)

                    # срабатывает если не удалось получить данные о видео на прошлой иттерации
                    self.streams_video_give.signal_processing.connect(
                        lambda: self.list_add_item(text="Попытка получения информации о видео", true_false=True))

                    # срабатывает если при проведении иттерации произошла ошибка
                    self.streams_video_give.signal_error.connect(
                        lambda: self.list_add_item(text="Попытка провалена", true_false=False))


                    # при завершенни метода в другом потоке из него выкидываются данные о стриме
                    self.streams_video_give.signal_alles.connect(self.check_streams)

                    # запуск метода в другом потоке
                    self.streams_video_give.start(priority=QThread.InheritPriority)

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


class streams_video_give_multithreads(QThread):
    signal_for_progressbar = pyqtSignal(int)  # для прогресс бара
    signal_error = pyqtSignal()  # для ошибок
    signal_processing = pyqtSignal()
    signal_alles = pyqtSignal(list or None)

    def __init__(self, url_video: str, parent=None):
        QThread.__init__(self, parent=parent)
        self.url = url_video

    @logger.catch()
    def run(self):
        self._streams = []
        self._range = 10
        for _ in range(self._range):
            try:
                self.signal_for_progressbar.emit(int((_ + 1) * 100 / self._range))
                self.signal_processing.emit()  # сигнал испускается если на прерыдущей иттерации произошла ошибка

                self._video_youtube = YouTube(self.url)
                time.sleep(0.5)
                self._streams = list(enumerate(self._video_youtube.streams.all()))

                """
                Гребаные цигнаские фокусы pytube: как я понял существует нерешенная проблема того, что нельзя получить видео с ограничениями по возрасту
                или какие то ограниченные видео. То есть даже если в цикл закинуть 200 повторений ничего не произойдет.
                Частичным решением данной проблемы является изменения клиента при инициализации класса в рабочих документах pytube:
                "Ваша папка\venv\Lib\site-packages\pytube\innertube.py" вот в этом файле в классе InnerTube в инициализаторе меняем client='ANDROID' на client='WEB'
                И тогда скорее всего все работать будет, но это не точно(
                """

                if self._streams:
                    break

            except Exception:
                self.signal_error.emit()  # испускается сигнал если произошла ошибка при получении стримов видео
                logger.error(traceback.format_exc())
                time.sleep(1.5)
        self.signal_alles.emit(
            self._streams)  # в конце в любом случае испускается сигнал содержащий данные стрима (даже если нон)


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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Programm_Window()
    ex.show()
    app.exec_()
