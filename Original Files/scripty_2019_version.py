# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'P:\ScriptyQt\gui_draft_design_3.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QCompleter, QApplication
from PyQt5.QtCore import QStringListModel
import os
import pyperclip
import pickle
import sys
import json
from PyQt5.QtCore import QThread
from time import sleep

# import ctypes
# myappid = 'scripty.1.0'  # arbitrary string
# ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

# TODO: facility for pushing updates automatically
# TODO: string list model from file contents
# TODO 1.1: List item hover = popup of script
# TODO 1.1: Live in system tray
# TODO 1.1: make tab widget resize with window? Depends on testing I think, whether users will try to resize or not
# TODO 1.1: parse Alex's snippets, add option to include in searches


def check_version():
    # include a check here to look for a newer version via the modified date of a newer file on the shared drive
    # then somehow delete this file and copy over the new one and then run the new one instead
    pass


def load_memories():
    try:
        with open('memories.pickle', 'rb') as file:
            x = pickle.load(file)
            print(x)
        return x
    except (FileNotFoundError, EOFError):
        with open('memories.pickle', 'wb') as file:
            d = {'root': '', 'search_choice': '', 'recents': [], 'freq_records': {}}
            pickle.dump(d, file)
        return d

# def get_root_path():
#     file = 'rememberer.txt'
#     try:
#         with open(file, 'r') as f:
#             memory = json.load(f)
#         return memory
#     except:
#         print("No 'rememberer.txt' file.")
#         return None


# def get_recents():
#     file = 'recents.txt'
#     try:
#         with open(file, 'r') as f:
#             memory = json.load(f)
#         return memory
#     except:
#         print("No 'recents.txt' file.")
#         return None


# def get_most_used():
#     file = 'most_used.txt'
#     try:
#         with open(file, 'r') as f:
#             memory = json.load(f)
#         return memory
#     except:
#         print("No 'most_used.txt' file.")
#         return None


def get_data(model, string_list):  # TODO: edit and QA, read triple quotes for context
    """Need to modify this to consume file titles and contents and create lists of individual words for using in the
    auto-completion."""
    model.setStringList(string_list)


# def save_root_path(root_file_path):
#     with open('config.txt', 'w') as f:  # contains the last root folder choice
#         contents = json.dumps(root_file_path)
#         f.write(contents)


# def save_to_recents(session_copies):  # TODO: QA
#     with open('recents.txt', 'w') as f:
#         """This needs to load the current recent list created from past sessions, and then modify it before writing
#         back to the file."""
#         try:
#             past_sessions = json.load(f)  # past_sessions will be a list of recents
#             for i in session_copies:  # session_copies is the copy operations from this session
#                 print(i)
#                 # does this item exist in the past_sessions list?
#                 if i in past_sessions:
#                     # if yes, delete it and then add it to the top of the list
#                     past_sessions.remove(i)
#                     past_sessions.append(i)
#                 else:
#                     # if no, add it to the top of the list
#                     past_sessions.append(i)
#             contents = json.dumps(past_sessions)
#             f.write(contents)
#         except:
#             print("The operation on 'recents.txt' did not succeed. Debug required.")


# def save_to_most_used(session_copies, most_used):  # TODO: QA
#     with open('most_used.txt', 'w') as f:
#         """This loads the copy records from the whole period of app use and updates the counts for each from the
#         current session."""
#         try:
#             for i in session_copies:
#                 if i in most_used:
#                     # find key(i) in most_used dict and add 1 to i
#                     most_used[i] += 1
#                 else:
#                     # add the key(i) and initialise with a value of 1
#                     most_used[i] = 1
#             # write to file here
#         except:
#             print("The operation on 'most_used.txt' did not succeed. Debug required.")


# class DisplayMessageThread(QThread):
#
#     def __init__(self):
#         QThread.__init__(self)
#
#     def run_func(self, ui_object):
#         ui_object.preview_pane.feedback_text.setText("Copied file to the clipboard!")
#         ui_object.update()
#         self.sleep(3)
#         ui_object.preview_pane.feedback_text.setText("")
#         ui_object.update()
#         self.terminate()


class CustomListWidget(QtWidgets.QListWidget):
    keyPressed = QtCore.pyqtSignal(int)

    def keyPressEvent(self, event):
        super(CustomListWidget, self).keyPressEvent(event)
        self.keyPressed.emit(event.key())


# noinspection PyAttributeOutsideInit,PyUnresolvedReferences
class UiMainWindow(object):

    # message_thread = DisplayMessageThread()

    memories = load_memories()
    keyPressed = QtCore.pyqtSignal(int)
    files = []
    search_choice = memories['search_choice']
    session_copies = memories['recents']  # need to make sure the order is right on this
    if memories is not None:
        freq_records = memories['freq_records']

    completer = QCompleter()
    model = QStringListModel()
    completer.setModel(model)

    show_preview = False

    def setup_ui(self, main_window, parent=None):
        main_window.setObjectName("main_window")
        main_window.resize(400, 250)
        self.central_widget = QtWidgets.QWidget(main_window)
        self.central_widget.setObjectName("central_widget")
        self.gridLayout = QtWidgets.QGridLayout(self.central_widget)
        self.gridLayout.setObjectName("gridLayout")

        # self.preview_pane = QtWidgets.QPlainTextEdit(self.central_widget)
        # self.preview_pane.setObjectName("preview_pane")
        # self.preview_pane.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        # self.gridLayout.addWidget(self.preview_pane, 1, 1, 1, 1)

        # self.preview_pane_label = QtWidgets.QLabel(self.central_widget)
        # self.preview_pane_label.setObjectName("preview_pane_label")
        # self.gridLayout.addWidget(self.preview_pane_label, 0, 1, 1, 1)

        self.tabWidget = QtWidgets.QTabWidget(self.central_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setAutoFillBackground(False)
        self.tabWidget.setObjectName("tabWidget")
        self.search_tab = QtWidgets.QWidget()
        self.search_tab.setObjectName("search_tab")
        self.formLayout = QtWidgets.QFormLayout(self.search_tab)
        self.formLayout.setObjectName("formLayout")
        self.search_by_label = QtWidgets.QLabel(self.search_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_by_label.sizePolicy().hasHeightForWidth())
        self.search_by_label.setSizePolicy(sizePolicy)
        self.search_by_label.setObjectName("search_by_label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.search_by_label)
        self.search_by = QtWidgets.QComboBox(self.search_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_by.sizePolicy().hasHeightForWidth())
        self.search_by.setSizePolicy(sizePolicy)
        self.search_by.setToolTipDuration(3)
        self.search_by.setMaxCount(10000)
        self.search_by.setObjectName("search_by")
        self.search_by.addItem("")
        self.search_by.setItemText(0, "")
        self.search_by.addItem("")
        self.search_by.addItem("")
        self.search_by.addItem("")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.search_by)
        self.search_text = QtWidgets.QLineEdit(self.search_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_text.sizePolicy().hasHeightForWidth())
        self.search_text.setSizePolicy(sizePolicy)
        self.search_text.setText("")
        self.search_text.setObjectName("search_text")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.SpanningRole, self.search_text)
        self.file_list = CustomListWidget(self.search_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.file_list.sizePolicy().hasHeightForWidth())
        self.file_list.setSizePolicy(sizePolicy)
        self.file_list.setMouseTracking(False)
        self.file_list.setObjectName("file_list")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.SpanningRole, self.file_list)
        self.copy_btn = QtWidgets.QPushButton(self.search_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.copy_btn.sizePolicy().hasHeightForWidth())
        self.copy_btn.setSizePolicy(sizePolicy)
        self.copy_btn.setMinimumSize(QtCore.QSize(0, 30))
        self.copy_btn.setObjectName("copy_btn")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.SpanningRole, self.copy_btn)
        self.exit_btn = QtWidgets.QPushButton(self.search_tab)
        self.exit_btn.setMinimumSize(QtCore.QSize(0, 30))
        self.exit_btn.setObjectName("exit_btn")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.SpanningRole, self.exit_btn)

        # settings tab
        self.tabWidget.addTab(self.search_tab, "")
        self.settings_tab = QtWidgets.QWidget()
        self.settings_tab.setObjectName("settings_tab")
        self.formLayout_3 = QtWidgets.QFormLayout(self.settings_tab)
        self.formLayout_3.setObjectName("formLayout_3")
        self.root_path_label = QtWidgets.QLabel(self.settings_tab)
        self.root_path_label.setObjectName("root_path_label")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.root_path_label)
        self.root_path = QtWidgets.QLineEdit(self.settings_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_by.sizePolicy().hasHeightForWidth())
        self.root_path.setSizePolicy(sizePolicy)
        self.root_path.setAlignment(QtCore.Qt.AlignRight)
        self.root_path.setObjectName("root_path")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.SpanningRole, self.root_path)
        self.folder_browse_btn = QtWidgets.QPushButton(self.settings_tab)
        self.folder_browse_btn.setObjectName("folder_browse_btn")
        self.formLayout_3.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.folder_browse_btn)
        self.show_preview_pane_checkbox = QtWidgets.QCheckBox(self.settings_tab)
        self.show_preview_pane_checkbox.setObjectName("see_preview_pane_checkbox")
        self.formLayout_3.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.show_preview_pane_checkbox)
        self.line = QtWidgets.QFrame(self.settings_tab)
        self.line.setMinimumSize(QtCore.QSize(1, 3))
        self.line.setLineWidth(10)
        self.line.setMidLineWidth(10)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.formLayout_3.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.line)
        self.tabWidget.addTab(self.settings_tab, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 2, 1)
        # self.feedback_text = QtWidgets.QLabel(self.central_widget)
        # self.feedback_text.setText("")
        # self.feedback_text.setObjectName("feedback_text")
        # self.gridLayout.addWidget(self.feedback_text, 2, 0, 1, 2)
        main_window.setCentralWidget(self.central_widget)
        self.menubar = QtWidgets.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 611, 21))
        self.menubar.setObjectName("menubar")
        main_window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)

        # clipbrd = QApplication.clipboard()

        self.retranslateUi(main_window)
        self.tabWidget.setCurrentIndex(0)
        self.search_by.setCurrentIndex(1)
        self.show_preview_pane_checkbox.toggled['bool'].connect(main_window.update)
        QtCore.QMetaObject.connectSlotsByName(main_window)

        main_window.setTabOrder(self.search_by, self.search_text)
        main_window.setTabOrder(self.search_text, self.file_list)
        main_window.setTabOrder(self.file_list, self.copy_btn)
        main_window.setTabOrder(self.copy_btn, self.exit_btn)
        # main_window.setTabOrder(self.exit_btn, self.preview_pane)

        self.exit_btn.clicked.connect(self.exit)
        self.folder_browse_btn.clicked.connect(self.browse_for_folder)
        self.copy_btn.clicked.connect(self.copy_file_to_clip)
        list(map(self.file_list.itemDoubleClicked.connect, [self.copy_file_to_clip]))
        self.search_text.textChanged.connect(self.filter_filelist)
        self.show_preview_pane_checkbox.stateChanged.connect(self.toggle_preview_pane)
        self.file_list.keyPressed.connect(self.on_key)  # TODO: Need to implement custom list class for this method
        self.file_list.itemSelectionChanged.connect(self.on_filename_selection)

    def retranslateUi(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "Scripty"))
        # main_window.closeEvent.connect(self.on_minimise)
        # self.preview_pane.setPlaceholderText(_translate("main_window", "Select a script and a preview will appear in this window...", "This is another potential comment, disambig"))
        # self.preview_pane_label.setText(_translate("main_window", "Snippet Preview"))
        self.search_by_label.setText(_translate("main_window", "Search by:"))
        self.search_by.setToolTip(_translate("main_window", "Determines what to look at when searching for files"))
        self.search_by.setCurrentText(_translate("main_window", "Title"))
        self.search_by.setItemText(0, _translate("main_window", "All"))
        self.search_by.setItemText(1, _translate("main_window", "Title"))
        self.search_by.setItemText(2, _translate("main_window", "Content"))
        self.search_by.setItemText(3, _translate("main_window", "Description"))
        self.search_text.setPlaceholderText(_translate("main_window", "Input search text..."))
        self.copy_btn.setText(_translate("main_window", "Copy to Clipboard"))
        self.exit_btn.setText(_translate("main_window", "Exit"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.search_tab), _translate("main_window", "Search"))
        self.root_path_label.setText(_translate("main_window", "Root Folder"))
        self.root_path.setText(_translate("main_window", "/home/james/PycharmProjects/PyQt-learn/Wikipedia Docs/"))
        self.folder_browse_btn.setText(_translate("main_window", "Browse"))
        self.show_preview_pane_checkbox.setText(_translate("main_window", "Show preview pane"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.settings_tab), _translate("main_window", "Settings"))
        root = self.memories['root']
        if root is not None:
            self.root_path.setText(_translate("main_window", root))
            self.set_filelist()
        else:
            self.root_path.setText(_translate("main_window", '/home/james/PycharmProjects/PyQt-learn/Wikipedia Docs/'))

        file_names = self.get_filelist()
        if file_names:
            get_data(self.model, file_names['file_names'])

    def browse_for_folder(self):
        folder_name = QFileDialog.getExistingDirectory(caption='Select directory')
        if folder_name:
            self.root_path.setText(folder_name)
            self.set_filelist()
            get_data(self.model, self.files[1])

    def remember(self):
        root_path = self.root_path.text()
        recents = self.session_copies
        full_records = self.freq_records
        search_choice = self.search_choice
        with open('memories.pickle', 'wb') as file:
            contents = {'root': root_path,
                        'search_choice': search_choice,
                        'recents': recents,
                        'freq_records': full_records
                        }
            pickle.dump(contents, file)

    def exit(self):
        self.remember()
        QtCore.QCoreApplication.instance().quit()

    def set_filelist(self):
        self.file_list.clear()
        if self.root_path.text():
            full_paths = []
            file_names = []
            for path, subdirs, files in os.walk(self.root_path.text()):
                for name in files:
                    full_paths.append(os.path.join(path, name))
                    file_names.append(os.path.join(name))
            self.files.append(full_paths)
            self.files.append(file_names)
            self.file_list.addItems(file_names)

    def get_filelist(self):
        if self.root_path.text():
            full_paths = []
            file_names = []
            for path, subdirs, files in os.walk(self.root_path.text()):
                for name in files:
                    full_paths.append(os.path.join(path, name))
                    file_names.append(os.path.join(name))
            return {'full_paths': full_paths, 'file_names': file_names}

    def get_filelist2(self, root, subdirs=True):
        """Gets a master list of files with full paths."""
        file_list = []
        if subdirs:
            for path, subdirs, files in os.walk(top=root):
                for name in files:
                    file_list.append({'file': name, 'full_path': os.path.join(path, name)})
        else:
            files = os.listdir(root)
            for name in files:
                file_list.append({'file': name, 'full_path': os.path.join(root, name)})
        # names = [x['file'].split('.')[0] for x in file_list]
        return file_list

    def copy_file_to_clip(self, it):
        """Find the index of the current item in the master list of short names, then get the matching index of the
        long path name.
        Add file name to records."""
        try:
            file_name = self.file_list.currentItem().text()
            ind = self.files[1].index(file_name)
            full_path = self.files[0][ind]
            with open(full_path, 'r') as f:
                contents = f.read()
            pyperclip.copy(contents)
            self.session_copies.append(file_name)
            print(f"Copied: {file_name}")
            if file_name in self.freq_records:
                self.freq_records[file_name] += 1
            else:
                self.freq_records[file_name] = 1
            self.statusbar.setStatusTip('Copied file to clipboard')
        except Exception:
            err = str(Exception)
            with open('CRASH_DUMP.txt', 'w') as f:
                f.write(err)

    def filter_filelist(self):
        """Limit list to appropriate items"""
        if self.search_text.text() == '':
            self.set_filelist()
            print("Empty search field")
        else:
            if str(self.search_by.currentText()) == 'Title':
                print("Filtering file list")
                print(self.search_by.currentText())
                print(self.search_text.text())
                self.file_list.clear()
                filtered_list = [i for i in self.files[1] if self.search_text.text() in i]
                self.file_list.addItems(filtered_list)

    def on_key(self, key):
        if key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            self.copy_file_to_clip(self.file_list.currentIndex())

    def on_filename_selection(self):
        """This function will be used to display the text of any selected files to the preview pane."""
        if self.show_preview is True:
            try:
                print("The user selected a file in the list and show_preview is True, updating preview pane.")
                file_name = self.file_list.currentItem().text()
                ind = self.files[1].index(file_name)
                full_path = self.files[0][ind]
                with open(full_path, 'r') as f:
                    contents = f.read()
                self.preview_pane.setPlainText(contents)
            except Exception:
                self.preview_pane.setPlainText('The file could not be read.')

    def toggle_preview_pane(self):
        if self.show_preview_pane_checkbox.isChecked():
            self.show_preview = True
            _translate = QtCore.QCoreApplication.translate

            self.preview_pane = QtWidgets.QPlainTextEdit(self.central_widget)
            self.preview_pane.setObjectName("preview_pane")
            self.preview_pane.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)

            self.preview_pane_label = QtWidgets.QLabel(self.central_widget)
            self.preview_pane_label.setObjectName("preview_pane_label")

            self.preview_pane.setPlaceholderText(
                _translate("main_window", "Select a script and a preview will appear in this window...",
                           "This is another potential comment, disambig"))
            self.preview_pane_label.setText(_translate("main_window", "Preview"))

            self.gridLayout.addWidget(self.preview_pane_label, 0, 1, 1, 1)
            self.gridLayout.addWidget(self.preview_pane, 1, 1, 1, 1)

            if self.file_list.selectedItems():
                self.on_filename_selection()

            # main_window.resize(600, 400)

            main_window.update()
            print(main_window.size())
        else:
            self.show_preview = False
            self.preview_pane_label.hide()
            self.preview_pane.hide()
            # main_window.resize(400, 250)
            main_window.update()
            print(main_window.size())

        # def on_minimise(self):
        #
        #     pass

        # def _create_tray(self):
        #     self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        #     self.tray_icon.activated.connect(self.__icon_activated)
        #
        # def __icon_activated(self, reason):
        #     if reason in (QtWidgets.QSystemTrayIcon.Trigger, QtWidgets.QSystemTrayIcon.DoubleClick):
        #         pass

        # TODO: load file names/file contents into a dict instead of a list, to allow for searching by file contents
        # TODO !!!: change the width of the root folder qlineedit box
        # TODO: allow for searching by file contents
        # TODO: allow writing inline preview edits back to the file
        # TODO: allow copying from the preview pane
        # TODO !!!: resize the window when showing/hiding the preview pane
        # TODO: add settings option for remain_on_top true/false
        # TODO !!!: add feedback when a file is copied i.e. item blink/flash or message display at base of window
        # TODO: refresh file list every x seconds... 10 seconds should be fine
        # TODO: add 'About' popup
        # TODO: implement a 'clear search' button

        # more than MVP stuff
        # TODO: implement Github repos as sources
        # TODO: implement Team Foundation (repos?) as sources


if __name__ == "__main__":
    # import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('ledger.ico'))
    main_window = QtWidgets.QMainWindow()
    main_window.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    ui = UiMainWindow()
    ui.setup_ui(main_window)
    main_window.show()
    ui.root_path.setFocus()
    sys.exit(app.exec_())
