from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle('My Window')

        label = QLabel('This is a label.')
        label.setAlignment(Qt.AlignCenter)

        self.setCentralWidget(label)

        toolbar = QToolBar('main toolbar')
        self.addToolBar(toolbar)

        button_action = QAction(QIcon('android.png'), 'your button', self)
        button_action.setStatusTip('this is your button')
        button_action.triggered.connect(self.onMyToolBarButtonClick)
        button_action.setCheckable(True)
        button_action.setShortcut(QKeySequence('Ctrl+p'))
        toolbar.addAction(button_action)

        toolbar.addSeparator()

        button_action2 = QAction(QIcon('arrow.png'), 'your button2', self)
        button_action2.setStatusTip('this is your button2')
        button_action2.triggered.connect(self.onMyToolBarButtonClick)
        button_action2.setCheckable(True)
        toolbar.addAction(button_action2)

        toolbar.addSeparator()

        toolbar.addWidget(QLabel('hello there'))

        toolbar.addSeparator()

        toolbar.addWidget(QCheckBox())

        self.setStatusBar(QStatusBar(self))

        menu = self.menuBar()
        # menu.setNativeMenuBar(False)

        file_menu = menu.addMenu('&File')
        file_menu.addAction(button_action)

        file_menu.addSeparator()

        file_submenu = file_menu.addMenu('submenu')

        file_submenu.addAction(button_action2)

    def onMyToolBarButtonClick(self, s):
        print('click', s)


def run():
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec_()


if __name__ == '__main__':
    run()
