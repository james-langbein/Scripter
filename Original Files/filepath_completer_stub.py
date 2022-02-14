from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import regex as re
import os

import sys

items = ['one', 'two', 'three']


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle('Filepath ')

        # walk dir tree and build matches that are not like the regex
        pattern = re.compile(r'[.].* | [.]gitignore')
        walker = os.walk('/home/james/')
        folders = []
        for dir in walker:
            if pattern.match(dir[0]):
                continue
            else:
                for subdir in dir[1]:
                    if not pattern.match(subdir):
                        if os.path.join(dir[0], subdir) not in folders:
                            folders.append(os.path.join(dir[0], subdir))

        completer = QCompleter()
        model = QStringListModel()
        completer.setModel(model)
        model.setStringList('list here')

        widget = QWidget()
        self.setCentralWidget(widget)


def run_app():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()


"""
The goal here is to build a model of the all the sub-directories from a root folder, and then provide QCompletions
when selecting the root folder in the GUI.
"""


def run():
    pattern1 = re.compile(r'\..*')
    walker = os.walk('/home/james/PycharmProjects/PyQt-learn', topdown=True)
    folders = []
    exclude = [pattern1]
    for root, dirs, files in walker:
        dirs[:] = [d for d in dirs if pattern1.match(d) not in exclude]
        tmp_folder = root.split('/')[-1]
        if pattern1.match(root.split('/')[-1]):
            continue
        else:
            for subdir in dirs:
                if not pattern1.match(subdir):
                    if os.path.join(root, subdir) not in folders:
                        folders.append(os.path.join(root, subdir))
    print(folders)


def run2():
    dummylst = ['.idea', 'Wikipedia Docs', 'subdir1']
    exclude = ['.idea']
    pattern1 = re.compile(r'\..*')
    pattern2 = re.compile(r'subdir1')
    exclude2 = [pattern1]
    lst2 = []
    for item in dummylst:
        matched = False
        for pattern in exclude2:
            if pattern.match(item):
                matched = True
            else:
                lst2.append(item)
    print(lst2)
    # dummylst[:] = [d for d in dummylst if  not in exclude2]
    # print(dummylst)


if __name__ == '__main__':
    run()
