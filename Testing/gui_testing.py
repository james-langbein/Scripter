from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
import sys


"""Testing using widgets for hiding/showing parts of the GUI"""


# noinspection PyUnresolvedReferences
class MainWindow(QMainWindow):

    # noinspection PyArgumentList
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # set min width appropriately
        self.setMinimumWidth(20)

        # init main layout
        self.main_layout = QHBoxLayout()

        # init vbox layouts
        self.vboxlayout1 = QVBoxLayout()
        self.vboxlayout2 = QVBoxLayout()

        # init widgets for vbox layouts - need to add to main layout later
        self.vboxwidget1 = QWidget()
        self.vboxwidget2 = QWidget()

        # set vbox widgets to contain vbox layouts
        self.vboxwidget1.setLayout(self.vboxlayout1)
        self.vboxwidget2.setLayout(self.vboxlayout2)

        # init inner widgets
        self.button1 = QPushButton(text='Button')
        self.button1.clicked.connect(self.show_hide_vbox2)
        self.label2 = QLabel(text='Label2')

        # add inner widgets to layouts
        self.vboxlayout1.addWidget(self.button1)
        self.vboxlayout2.addWidget(self.label2)

        # add vbox widgets to main layout
        self.main_layout.addWidget(self.vboxwidget1)
        self.main_layout.addWidget(self.vboxwidget2)

        # initialise main widget
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

    def show_hide_vbox2(self):
        print(f'Vbox widgets detail is: {self.vboxwidget1.childrenRect()}')
        bx, by, bw, bh = self.button1.x(), self.button1.y(), self.button1.width(), self.button1.height()
        if self.vboxwidget2.isVisible():
            print(f'Geometry before resize: {self.geometry()}')
            x, y, w, h = self.x(), self.y(), self.width(), self.height()
            print(f'Button width before resize: {self.button1.width()}')
            print(f'Vbox widget width before resize: {self.vboxwidget1.width()}')
            self.vboxwidget2.hide()
            self.setGeometry(x+1, y+31, w/2, h)
            self.button1.setGeometry(bx, by, bw, bh)
        elif not self.vboxwidget2.isVisible():
            print(f'Geometry before resize: {self.geometry()}')
            x, y, w, h = self.x(), self.y(), self.width(), self.height()
            print(f'Button width before resize: {self.button1.width()}')
            print(f'Vbox widget width before resize: {self.vboxwidget1.width()}')
            self.setGeometry(x+1, y+31, w*2, h)
            self.button1.setGeometry(bx, by, bw, bh)
            self.vboxwidget2.show()
        print(f'Geometry after resize: {self.geometry()}\n')
        print(f'Button width after resize: {self.button1.width()}')
        print(f'Vbox widget width after resize: {self.vboxwidget1.width()}')


def run():
    # noinspection PyArgumentList

    app = QApplication(sys.argv)
    # app.setWindowIcon(QIcon('blue_icon.png'))

    window = MainWindow()
    window.setWindowFlags(Qt.WindowStaysOnTopHint)
    window.show()
    app.exec_()


if __name__ == '__main__':
    run()
