from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import sys

items = ['one', 'two', 'three']


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle('My Window')

        layout = QStackedLayout()

        layout.addWidget()

        widget = QWidget()
        self.setCentralWidget(widget)


def run():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()


if __name__ == '__main__':
    run()
