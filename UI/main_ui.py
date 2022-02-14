import os
import pickle
import re
# import copy
import sys
from ctypes import windll

import pyperclip
import spacy
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from browser import Browser
from source import Source
from document import Document
from corpus import Corpus

# tell Windows that this app has a specific custom ID, thus leading to the correct icon being shown in the taskbar
myappid = u'jrldevelopment.scripter.beta'
windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

# load nlp, used in get_corpus method
nlp = spacy.load('en_core_web_sm')
nlp.disable_pipes(['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'ner', 'lemmatizer'])

# the below variables will eventually become config options in the application
filelist_root = 'C:\\Users\\JamesLangbein\\All\\SQL Scripts'
# index_root = True
case_sensitivity = True
# index_files = True
# contents_index = None
# filename_suffixes = False
# search_subdirectories = True
icon_file = 'Icons/blue_icon2.png'
pickle_file = '../Cache/canope.pkl'
window_title = 'Scripter - Beta'


# noinspection PyUnresolvedReferences
# noinspection PyArgumentList
class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # TODO: get pickled config options and set below flags...
        #  - position/size
        #  - app options
        # TODO: add 'window stays on top' to configurable options
        # TODO: search by 'most used' option, sorts files in order of most used
        # TODO: File menu > add option 'Reload File List'
        # TODO: 'exclude folders' config option? exclusive 'include folders' option? (line edit lists)

        self.flag_force_quit = False
        self.flag_minimise_to_tray = False
        self.flag_show_preview = True
        self.flag_file_updated = True
        self.flag_preview_edited = False

        self.setWindowTitle(window_title)
        self.setWindowIcon(QIcon(icon_file))

        # https://www.hongkiat.com/blog/40-free-and-useful-gui-icon-sets-for-web-designers/
        # https://iconstore.co/icons/72-free-icons/

        # init/connect actions
        action_show = QAction('Show', self)
        action_show.triggered.connect(self.show)
        action_hide = QAction('Hide', self)
        action_hide.triggered.connect(self.hide)
        action_quit = QAction('Quit', self)
        action_quit.triggered.connect(self.force_quit)
        action_about = QAction('About', self)
        action_about.triggered.connect(self.show_about_window)
        action_config = QAction('Preferences...', self)
        action_config.triggered.connect(self.show_config_window)
        action_new_file = QAction('New File', self)
        action_new_file.triggered.connect(self.create_new_file)
        action_copy = QAction('Copy', self)
        # action_copy.setShortcut(QShortcut(QKeySequence(Qt.CTRL, Qt.Key_C)))
        action_copy.triggered.connect(self.copy_button_clicked)
        # TODO: change various hardcoded function names to actions...

        # init system tray menu and icon
        self.menu_systray = QMenu()
        self.menu_systray.addAction(action_show)
        self.menu_systray.addAction(action_hide)
        self.menu_systray.addAction(action_quit)
        self.icon_systray = QSystemTrayIcon(QIcon(icon_file), parent=self)
        self.icon_systray.setToolTip(window_title)
        self.icon_systray.setContextMenu(self.menu_systray)
        self.icon_systray.activated.connect(self.show)
        self.icon_systray.show()

        # init search string completion model
        file_completer = QCompleter()
        file_model = QStringListModel()
        file_completer.setModel(file_model)

        # init menus
        menubar = self.menuBar()
        menu_file = menubar.addMenu('&File')
        menu_edit = menubar.addMenu('&Edit')  # do I need an edit menu...
        menu_options = menubar.addMenu('&Options')
        menu_help = menubar.addMenu('&Help')

        menu_options.addAction(action_config, text='Preferences...')
        menu_help.addAction(action_about, text='About...')
        menu_edit.addAction(action_new_file, text='New File...')

        self.current_script_parameters_labels = None
        self.current_script_parameters_widgets = None

        # toolbar (for mini-buttons...)
        # toolbar = QToolBar('The Toolbar')
        # self.addToolBar(toolbar)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # specify layouts - main window layout
        self.layout_main_hbox = QHBoxLayout()
        # main_layout sections
        self.layout_search_pane_vbox = QVBoxLayout()
        sizePolicy = QSizePolicy()
        self.layout_preview_pane_vbox = QVBoxLayout()
        # children of main_layout sections
        self.layout_search_by_hbox = QHBoxLayout()
        self.layout_search_widgets_vbox = QVBoxLayout()
        self.layout_preview_text_vbox = QVBoxLayout()
        self.layout_preview_buttons_hbox = QHBoxLayout()
        # add children to main_layout
        self.layout_search_pane_vbox.addLayout(self.layout_search_by_hbox)
        self.layout_search_pane_vbox.addLayout(self.layout_search_widgets_vbox)
        self.layout_preview_pane_vbox.addLayout(self.layout_preview_text_vbox)
        self.layout_preview_pane_vbox.addLayout(self.layout_preview_buttons_hbox)
        self.layout_main_hbox.addLayout(self.layout_search_pane_vbox)
        # specify search_pane_layout widgets
        self.label_search_by = QLabel('Search by: ')
        self.label_search_by.setMaximumWidth(50)
        # search by dropdown
        self.combobox_search_by = QComboBox()
        # self.combobox_search_by.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))
        self.combobox_search_by.setMaximumWidth(100)
        self.combobox_search_by.addItems(['Filename', 'File Contents'])
        self.combobox_search_by.setCurrentIndex(0)
        # TODO: put a spacer in between combobox and preview checkbox
        # self.search_spacer_one = Q
        # preview checkbox
        self.checkbox_show_preview = QCheckBox('Preview')
        self.checkbox_show_preview.toggled.connect(self.preview_checkbox_toggled)
        # file list
        self.list_fileview = QListWidget()
        self.list_fileview.installEventFilter(self)
        self.list_fileview.itemSelectionChanged.connect(self.on_filelist_item_selected)
        self.list_fileview.itemDoubleClicked.connect(self.copy_button_clicked)
        self.list_fileview.setMouseTracking(True)
        # file list separator (for 'Most Used' option, separate > 0 count from 0 count items)
        # see https://stackoverflow.com/questions/24671636/qt-qlistwidget-separator-line-after-particuler-items
        # implement if requested later
        # self.fileview_separator_item.setSizeHint(QSize(0, 0))
        # self.fileview_separator_frame = QFrame()
        # self.fileview_separator_frame.setFrameShape(QFrame.HLine)
        # search by text
        self.lineEdit_search_by_text = QLineEdit()
        self.lineEdit_search_by_text.installEventFilter(self)
        self.lineEdit_search_by_text.setPlaceholderText('Search filter...')
        # copy to clipboard button
        # self.fileview_separator_item = QListWidgetItem()
        # self.fileview_separator_item.setFlags(Qt.NoItemFlags)
        self.lineEdit_search_by_text.textChanged.connect(self.filter_filelist_view)
        self.button_copy = QPushButton(text='Copy to Clipboard')
        self.button_copy.setStatusTip('Copy selected file. Alternatively press Enter while a file is selected.')
        self.button_copy.clicked.connect(self.copy_button_clicked)
        # new file button
        self.button_new_file = QPushButton(text='New File')
        self.button_new_file.setStatusTip('Create a new text file.')
        self.button_new_file.clicked.connect(self.create_new_file)
        # exit button
        # self.exit_button = QPushButton(text='Exit')
        # self.exit_button.setStatusTip('Exit to system tray.')
        # self.exit_button.clicked.connect(self.close)
        # test button
        # self.test_button = QPushButton(text='Testing Button')
        # self.test_button.setStatusTip('Copy selected file.')
        # self.test_button.clicked.connect(self.testing_function)

        # specify preview_layout widgets
        # self.preview_title_label = QLabel('Preview')
        # preview_text
        # TODO: implement syntax-colouring for parameters
        self.textEdit_preview = QTextEdit()
        self.textEdit_preview.setPlaceholderText('Select a file from the list to preview the contents...')
        self.textEdit_preview.setLineWrapMode(QTextEdit.WidgetWidth)  # NoWrap, WidgetWidth
        self.textEdit_preview.cursorPositionChanged.connect(self.set_preview_edited_flag)
        # preview buttons
        # set parameters button
        self.button_set_params = QPushButton(text='Set Parameters')
        self.button_set_params.setStatusTip('Open a window to fill out the parameters found in this script.')
        self.button_set_params.clicked.connect(self.set_script_parameters)
        # save edits button
        self.button_save_edits = QPushButton(text='Save Edits')
        self.button_save_edits.setStatusTip('Save the current preview edits to the selected file.')
        self.button_save_edits.clicked.connect(self.update_file)  # updates the actual file and the corpus
        # undo edits button
        self.button_undo_edits = QPushButton(text='Clear Edits')
        self.button_undo_edits.setStatusTip('Reset the preview text to the original file content.')
        self.button_undo_edits.clicked.connect(self.on_filelist_item_selected)
        # add search_pane_layout widgets
        self.layout_search_by_hbox.addWidget(self.label_search_by)
        self.layout_search_by_hbox.addWidget(self.combobox_search_by)
        self.layout_search_by_hbox.addStretch()
        self.layout_search_by_hbox.addWidget(self.checkbox_show_preview)
        self.layout_search_widgets_vbox.addWidget(self.lineEdit_search_by_text)
        self.layout_search_widgets_vbox.addWidget(self.list_fileview)
        self.layout_search_widgets_vbox.addWidget(self.button_copy)
        self.layout_search_widgets_vbox.addWidget(self.button_new_file)
        # add preview_layout widgets
        self.layout_preview_text_vbox.addWidget(self.textEdit_preview)
        self.layout_preview_text_vbox.addWidget(self.button_set_params)
        self.layout_preview_buttons_hbox.addWidget(self.button_undo_edits)
        self.layout_preview_buttons_hbox.addWidget(self.button_save_edits)

        # new file dialogue
        self.dialogue_new_file = QDialog(self)
        self.dialogue_new_file.setWindowTitle('Create New File')
        # new file layout
        self.layout_new_file_vbox = QVBoxLayout()
        # new file sections
        self.layout_folder_select_hbox = QHBoxLayout()
        self.layout_filename_hbox = QHBoxLayout()
        self.layout_filecontent_vbox = QVBoxLayout()
        # add children to new_file_layout
        self.layout_new_file_vbox.addLayout(self.layout_folder_select_hbox)
        self.layout_new_file_vbox.addLayout(self.layout_filename_hbox)
        self.layout_new_file_vbox.addLayout(self.layout_filecontent_vbox)
        # specify new_file widgets
        self.label_folder = QLabel(text='Folder:')
        self.lineEdit_new_file_folder = QLineEdit()
        self.lineEdit_new_file_folder.setText(filelist_root)
        self.button_select_folder = QPushButton(text='Select Folder')
        self.button_select_folder.clicked.connect(self.pick_newfile_folder)
        self.label_input_filename = QLabel(text='Filename:')
        self.input_filename_widget = QLineEdit()
        self.input_filename_widget.setPlaceholderText('Input file name...')
        self.input_filename_widget.setFocus()  # TODO: post-MVP, make this the selected widget on window load?
        self.input_filecontent_label = QLabel(text='Text:')
        self.input_filecontent_widget = QTextEdit()
        self.save_file_button = QPushButton(text='Save New File')
        self.save_file_button.clicked.connect(self.save_new_file)
        # TODO: implement exit button for the new_file_dialogue
        # add new_file widgets to new_file layouts
        self.layout_folder_select_hbox.addWidget(self.label_folder)
        self.layout_folder_select_hbox.addWidget(self.lineEdit_new_file_folder)
        self.layout_folder_select_hbox.addWidget(self.button_select_folder)
        self.layout_filename_hbox.addWidget(self.label_input_filename)
        self.layout_filename_hbox.addWidget(self.input_filename_widget)
        self.layout_filecontent_vbox.addWidget(self.input_filecontent_label)
        self.layout_filecontent_vbox.addWidget(self.input_filecontent_widget)
        self.layout_new_file_vbox.addWidget(self.save_file_button)
        self.dialogue_new_file.setLayout(self.layout_new_file_vbox)

        # script parameters dialogue
        self.dialogue_script_parameters = QDialog(self)
        self.dialogue_script_parameters.setWindowTitle('File Parameters')
        # layouts
        self.layout_script_parameters_vbox = QVBoxLayout()  # main layout
        self.layout_script_parameters_label_hbox = QHBoxLayout()  # for the title label
        self.layout_custom_params_form = QFormLayout()
        self.layout_insert_parameters_button_hbox = QHBoxLayout()
        # widgets
        self.label_parameters_title = QLabel(text='Input Parameter Values')
        self.button_insert_parameters = QPushButton(text='Insert into Script')
        self.button_insert_parameters.clicked.connect(self.insert_parameters)
        # add widgets to layouts
        self.layout_script_parameters_label_hbox.addWidget(self.label_parameters_title)
        self.layout_insert_parameters_button_hbox.addWidget(self.button_insert_parameters)
        # each script parameter will be dynamically added during exec
        # add child layouts to parents
        self.dialogue_script_parameters.setLayout(self.layout_script_parameters_vbox)
        self.layout_script_parameters_vbox.addLayout(self.layout_script_parameters_label_hbox)
        self.layout_script_parameters_vbox.addLayout(self.layout_custom_params_form)
        self.layout_script_parameters_vbox.addLayout(self.layout_insert_parameters_button_hbox)

        # preferences dialogue
        self.dialogue_preferences = QDialog(self)
        self.dialogue_preferences.setWindowTitle('Preferences')
        self.dialogue_preferences.setMinimumWidth(200)
        # layouts
        self.layout_preferences_dialogue = QFormLayout()
        self.layout_general_preferences = QVBoxLayout()
        self.layout_search_preference = QVBoxLayout()
        self.layout_ok_cancel = QHBoxLayout()
        # groupboxes
        self.groupbox_general_preferences = QGroupBox('General')
        self.groupbox_general_preferences.setLayout(self.layout_general_preferences)
        self.groupbox_search_ordering = QGroupBox('Order Search Results by')
        self.groupbox_search_ordering.setLayout(self.layout_search_preference)
        # general widgets  TODO: connect items to actions/functions
        self.checkbox_quit_to_systray = QCheckBox('Exit to System Tray')
        self.checkbox_window_stays_on_top = QCheckBox('Window Stays on Top')
        self.checkbox_include_file_suffixes = QCheckBox('Include File Suffixes')
        self.checkbox_case_sensitive_search = QCheckBox('Case Sensitive Search')
        # TODO: give a dropdown for choosing the colour of parameter highlighting
        # https://stackoverflow.com/questions/26679515/how-to-update-qsyntaxhighlighter-color-coding-when-user-changes-text
        # TODO: if requested enough, implement highlighting of code depending on file suffix
        # search results widgets
        self.radio_search_alphabetical = QRadioButton('Alphabetical')
        self.radio_search_most_used = QRadioButton('Most Used')
        # ok/cancel widgets
        self.ok_preferences = QPushButton('Ok')
        self.cancel_preferences = QPushButton('Cancel')
        # add widgets to General Preferences group
        self.layout_general_preferences.addWidget(self.checkbox_quit_to_systray)
        self.layout_general_preferences.addWidget(self.checkbox_window_stays_on_top)
        self.layout_general_preferences.addWidget(self.checkbox_include_file_suffixes)
        # add search widgets to Search group
        self.layout_search_preference.addWidget(self.radio_search_alphabetical)
        self.layout_search_preference.addWidget(self.radio_search_most_used)
        # add groups to main layout
        self.layout_preferences_dialogue.addWidget(self.groupbox_general_preferences)
        self.layout_preferences_dialogue.addWidget(self.groupbox_search_ordering)
        # self.lineEdit_exclude_folders = QLineEdit()  # TODO: turn this into grid/list dialogue later?
        # TODO: add OK and Cancel buttons
        # TODO: add line edit for choosing which file types to show based on file suffix
        # add widgets to layout
        # self.layout_preferences_dialogue.addWidget(self.checkbox_quit_to_systray)
        # self.layout_preferences_dialogue.addWidget(self.checkbox_window_stays_on_top)
        # self.layout_preferences_dialogue.addWidget(self.checkbox_include_file_suffixes)
        # self.layout_preferences_dialogue.addWidget(self.lineEdit_exclude_folders)
        # add child layouts to parents
        self.dialogue_preferences.setLayout(self.layout_preferences_dialogue)

        # TODO: set all the preferences here based on pickled info
        self.checkbox_quit_to_systray.setCheckState(Qt.CheckState.Checked)
        self.checkbox_window_stays_on_top.setCheckState(Qt.CheckState.Checked)
        self.checkbox_include_file_suffixes.setCheckState(Qt.CheckState.Checked)
        self.checkbox_case_sensitive_search.setCheckState(Qt.CheckState.Checked)
        self.radio_search_most_used.setChecked(True)  # TODO: move to 'set preferences' section later

        # check saved flag_show_preview and set checkState accordingly
        if self.flag_show_preview:  # TODO: change this to checking the saved/loaded prefs
            self.checkbox_show_preview.setCheckState(Qt.CheckState.Checked)
        # check show_preview_flag and show preview pane if True
        if self.flag_show_preview is True:
            self.layout_main_hbox.addLayout(self.layout_preview_pane_vbox)

        # initialise main widget
        widget = QWidget()
        widget.setLayout(self.layout_main_hbox)
        self.setCentralWidget(widget)

        # initialise the corpus
        self.corpus = None
        self.update_corpus(filelist_root)  # sets the corpus value in line above

        # initialise the bm25 indices (not being used due to inconsistent search results)
        # self.bm25_filenames = BM25Okapi([x['title_tokens'] for x in self.corpus])
        # self.bm25_filecontents = BM25Okapi([x['content_tokens'] for x in self.corpus])

        # keep a full filelist for when the query lineEdit is completely cleared, avoids recalculation each time
        self.full_filelist = [item['title'] for item in self.corpus]

        # keep a sorted filelist for when Most Used by is on  # TODO: delete once single corpus implemented
        self.sorted_corpus = sorted([item for item in self.corpus], key=lambda x: x['copy_count'], reverse=True)
        self.full_filelist_sorted = [item['title'] for item in self.sorted_corpus]
        # self.full_filelist_sorted.sort(key=lambda x: x['copy_count'], reverse=True)

        # will be set to a list of items from the corpus, begins with all items
        self.filtered_corpus = self.corpus

        # will be set to a list of filenames from filtered_filelist
        self.filtered_filelist_names = [item['title'] for item in self.filtered_corpus]

        # initialise list_fileview with file names list
        if self.radio_search_most_used.isChecked():
            self.list_fileview.addItems(self.full_filelist_sorted)
        elif self.radio_search_alphabetical.isChecked():
            self.list_fileview.addItems(self.filtered_filelist_names)

        # TODO: after MVP, depending on requests, implement file tagging...

    # functions (reorganise later)
    # @staticmethod
    # def set_model_stringlist(model, strlist):
    #     model.setStringList(strlist)

    def eventFilter(self, source, event):
        # print('\nEntering eventFilter function.')
        if event.type() == QEvent.KeyPress and event.matches(QKeySequence.InsertParagraphSeparator) \
                and source is self.lineEdit_search_by_text and self.list_fileview.count() == 1:
            pyperclip.copy(self.filtered_corpus[0]['content'])
        elif event.type() == QEvent.KeyPress and event.matches(QKeySequence.InsertParagraphSeparator):
            self.copy_button_clicked()
        elif event.type() == QEvent and self.lineEdit_search_by_text == '':
            self.filter_filelist_view()
        # elif event.type() == QEvent and event == QKeySequence(Qt.CTRL + Qt.Key_AsciiTilde):
        #     print('Ctrl + ` pressed.')
        # else:
        #     print('Caught event and exited through else statement.')
        return super().eventFilter(source, event)

    def show_about_window(self):
        print('\nEntering show_about_window function...')
        print('Selected menu option to show the About window.')

    def show_config_window(self):
        print('\nEntering show_config_window function...')
        print('Selected menu option to show the Configuration window.')
        self.dialogue_preferences.exec_()

    def preview_checkbox_toggled(self, state):
        print('\nEntering preview_checkbox_toggled function...')
        # TODO: window changing size again... fix
        print(f'Geometry before resize: {self.geometry()}')
        x, y, w, h = self.x(), self.y(), self.width(), self.height()
        if state:  # show layout
            print('Showing preview pane.')
            self.setGeometry(x+1, y+31, w*2, h)
            self.layout_main_hbox.addLayout(self.layout_preview_pane_vbox)
            self.textEdit_preview.setVisible(True)
            self.button_save_edits.setVisible(True)
            self.button_set_params.setVisible(True)
        elif not state:  # hide layout
            print('Hiding preview pane.')
            self.setGeometry(x+1, y+31, w/2, h)
            self.textEdit_preview.setVisible(False)
            self.button_save_edits.setVisible(False)
            self.button_set_params.setVisible(False)
            self.layout_main_hbox.removeItem(self.layout_preview_pane_vbox)
        print(f'Geometry after resize: {self.geometry()}\n')

    # def reset_preview_edits(self):
    #     """Reset the preview text to the original file content."""
    #     current_row =

    def set_preview_edited_flag(self):
        """This will be changed during two events:
        1. Content being updated by filelist view item selection. This change is manually in by the item selection
        slot, as this flag is only for manual typing but I don't know if it's possible to distinguish between the two.
        2. Manual typing, in which case the below change to True will be kept.

        In the event that manual typing occurs and then the edits are saved to file, the save slot will manually revert
        the flag to False.

        The flag affects the statusbar message shown when the Copy button is clicked.
        False = 'File content copied to clipboard'
        True = 'Temporary edits detected, preview content copied to clipboard'
        """
        self.flag_preview_edited = True

    def update_corpus(self, root):  # TODO: implement multiple root sources...
        """Assumes that recursive subdirectory search is always desired.
        Only supports Windows file system searching."""
        print('\nEntering update_corpus function...')
        # check if filelist_root is set, if not then return message
        if not filelist_root:
            return 'Filelist_root not set, exiting'

        else:
            # does pickled corpus exist?
            if os.path.exists(pickle_file):
                # yes, load pickled corpus
                print('Pickled corpus exists, loading into memory.')
                with open(pickle_file, 'rb') as pkl:
                    self.corpus = pickle.load(pkl)

            # if pickled corpus does not exist > set corpus to empty list
            else:
                print('No pickled corpus, creating empty corpus.')
                self.corpus = []

            # check each file in corpus against content of actual files, update if necessary
            # if corpus is empty list this block will be passed without failure
            print('Checking corpus entries against file-system.')
            for key, file in enumerate(self.corpus):
                pickled_filecontent = file['content']
                full_filename = os.path.join(file['folder_path'], file['title'])
                if os.path.exists(full_filename):  # check file still exists before trying to open it
                    with open(full_filename, 'r') as f:
                        actual_content = f.read()
                        if actual_content == pickled_filecontent:  # file exists with same name and content, ignore
                            pass
                        else:  # file exists but with different content, update corpus record
                            file['content'] = actual_content
                else:  # file doesn't exist anymore, remove entry from corpus
                    print('File not found, deleting from corpus.')
                    print(file)
                    del(self.corpus[key])

            # then walk the filesystem to check for files not in the corpus
            print('Checking file-system for files that don\'t exist in the corpus.')
            for path, subdirs, files in os.walk(top=root):
                for filename in files:
                    if os.path.join(path, filename) not in [x['full_path'] for x in self.corpus]:
                        # load those files into the corpus
                        folder_path = path
                        title = filename
                        title_tokens = filename.split('.')[0].split(' ')
                        with open(os.path.join(path, filename), 'r', encoding='UTF-8') as f:
                            try:
                                content = f.read()
                                content.replace('--', '')
                                doc = nlp(content)
                                content_tokens = set([token.text.lower() for token in doc if token.is_alpha])
                            except Exception as e:
                                print(f, e)
                        last_modified = os.path.getmtime(path)

                        self.corpus.append({
                            'folder_path': folder_path,
                            'title': title,
                            'full_path': folder_path + '\\' + title,
                            'title_tokens': title_tokens,
                            'content': content,
                            'content_tokens': content_tokens,
                            'last_modified': last_modified,
                            'copy_count': 0
                        })

        # sort the corpus by file title alphabetically ignoring case
        self.corpus.sort(key=lambda k: k['title'].lower())
        print(f'Loaded corpus: {len(self.corpus)} files.')
        return 'Success.'

    def update_file(self):
        """Needs to update the real file as well as self.corpus entry.
        Also set file_updated flag to True, this indicates that the corpus should be repickled on exit."""
        print('\nEntering update_corpus function...')

        current_row = self.list_fileview.currentRow()
        full_filepath = self.filtered_corpus[current_row]['full_path']
        edited_text = self.textEdit_preview.toPlainText()

        # try updating the actual file
        try:
            with open(full_filepath, 'w') as file:
                file.write(edited_text)
                self.flag_file_updated = True

            # if succeeded then continue and update corpus so that it always mirrors actual files
            self.filtered_corpus[current_row]['content'] = edited_text

            print('File and corpus updated.')
            self.statusbar.showMessage('File updated.', 10000)

            # false as now any copy actions are coming 'from the file' from the users perspective
            self.flag_preview_edited = False

        # if failed then exit gracefully with message and don't update corpus entry
        except Exception as e:
            # TODO: implement logging of errors, plus show dialogue on failure to notify me
            print('Failed to update file, did not update corpus.')
            print(e)

    def create_new_file(self):
        """Create new file for a script/template. Will show dialogue to choose parent folder and give filename, then
        present a TextEdit window to copy/type the text into, then a Save New File button."""
        print('\nEntering create_new_file function. (Calling exec on the new_file_dialogue)')
        self.dialogue_new_file.exec_()

    def pick_newfile_folder(self):
        print('\nEntering pick_newfile_folder function...')
        dialog = QFileDialog()
        folder_path = dialog.getExistingDirectory(None, "Select Folder", dir=filelist_root)
        self.lineEdit_new_file_folder.setText(folder_path)

    def save_new_file(self):
        """Save the file with folder/filename/content as specified.
        Check for empty values first, then try to save if filled out."""
        print('\nEntering save_new_file function...')
        if not self.lineEdit_new_file_folder.text() \
            or not self.input_filename_widget.text() \
                or not self.input_filecontent_widget.toPlainText():
            print('New file save failed due to empty field.')
            self.statusbar.showMessage('File save failed due to empty field.', 10000)
        else:
            # try saving the file
            # TODO: how do I handle presence/lack of file suffix? Dropdown with options?
            try:
                folder_path = self.lineEdit_new_file_folder.text()
                file_name = self.input_filename_widget.text()
                file_content = self.input_filecontent_widget.toPlainText()
                with open(os.path.join(folder_path, file_name), 'w') as file:
                    file.write(file_content)
                self.update_corpus(filelist_root)
                self.statusbar.showMessage(f'Saved new file.', 10000)
            except Exception as e:
                print(e)

    def set_script_parameters(self):
        """Find the parameters in the current previewed file and open the Set Script Parameters window."""
        print('\nEntering set_script_parameters function...')
        self.current_script_parameters_labels = re.findall(r'<([\w _]*)>', self.textEdit_preview.toPlainText())
        if len(self.current_script_parameters_labels) == 0:
            self.statusbar.showMessage('No parameters found')
        else:
            self.current_script_parameters_widgets = []
            print(self.current_script_parameters_labels)
            for key, param in enumerate(self.current_script_parameters_labels):
                label = QLabel(text=f'{param}:')
                label.deleteLater()
                globals()[f'parameter_var_{param}'] = QLineEdit()
                globals()[f'parameter_var_{param}'].deleteLater()
                self.layout_custom_params_form.addRow(label, globals()[f'parameter_var_{param}'])
                self.current_script_parameters_widgets.append(globals()[f'parameter_var_{param}'])
            self.dialogue_script_parameters.exec_()

    def insert_parameters(self):
        print('\nEntering insert_parameters function...')
        text = self.textEdit_preview.toPlainText()
        text_as_bytes = bytes(text, 'unicode_escape')
        for key, value in enumerate(self.current_script_parameters_widgets):
            user_input = value.text()
            user_input_as_bytes = bytes(user_input, 'unicode_escape')
            print(user_input)
            print(f'Replacing value {value.text()}...')
            query = '<' + self.current_script_parameters_labels[key] + '>'
            query = query.encode('unicode_escape')
            # if '\\' in query:
            #     query.replace('\\', '\\\\')
            print(query)
            pattern = re.compile(query)
            text_as_bytes = re.sub(pattern, user_input_as_bytes, text_as_bytes)
        self.textEdit_preview.setText(text_as_bytes.decode('unicode_escape'))
        self.current_script_parameters_labels = []
        self.current_script_parameters_widgets = []
        self.dialogue_script_parameters.close()
        self.statusbar.showMessage('Inserted temporary parameters')

    # TODO (post-Beta): periodically (every x seconds) check the file system for new files and load into the
    #  corpus/filelist view, separate thread...

    def on_filelist_item_selected(self):
        print('\nEntering on_filelist_item_selected function...')
        print(f'Clicked list item: {self.list_fileview.currentItem().text()}\nSetting preview_text to file content.')
        current_row = self.list_fileview.currentRow()
        if self.radio_search_most_used.isChecked():
            file_content = self.sorted_corpus[current_row]['content']
        else:
            file_content = self.filtered_corpus[current_row]['content']
        self.textEdit_preview.setText(file_content)
        self.flag_preview_edited = False  # required to reset the flag following a non-manual-typing update

    def copy_button_clicked(self):
        # TODO: need to implement usage of a single base corpus to more easily maintain metadata like no. of copies
        # TODO: re-sort the corpus after a copy operation
        print('\nEntering copy_button_clicked function...')
        if self.list_fileview.currentRow() == -1:
            print('No item selected. Setting statusbar message.')
            self.statusbar.showMessage('Please select an item from the list')
        else:
            if self.list_fileview.count() > 1:
                try:
                    if self.radio_search_alphabetical.isChecked():
                        print('Alphabetical ordering identified, using Filtered Corpus')
                        print(f'Current row is: {self.list_fileview.currentRow()}')
                        if self.textEdit_preview.toPlainText():
                            print('Getting file content from preview.')
                            file_content = self.textEdit_preview.toPlainText()
                        else:
                            print('Getting file content from corpus.')
                            file_content = self.filtered_corpus[self.list_fileview.currentRow()]['content']

                        print('Copying file to clipboard.')
                        pyperclip.copy(file_content)

                        print('Increasing copy count.')
                        self.filtered_corpus[self.list_fileview.currentRow()]['copy_count'] += 1
                        print(f'Copy count of file now: '
                              f'{self.filtered_corpus[self.list_fileview.currentRow()]["copy_count"]}')

                        if self.flag_preview_edited:
                            self.statusbar.showMessage('Temporary edits detected, preview content copied to clipboard')
                        else:
                            self.statusbar.showMessage('Copied file content to clipboard')
                    elif self.radio_search_most_used.isChecked():
                        print('Most Used First ordering identified, using Sorted Corpus.')
                        print(f'Current row is: {self.list_fileview.currentRow()}')
                        if self.textEdit_preview.toPlainText():
                            print('Getting file content from preview.')
                            file_content = self.textEdit_preview.toPlainText()
                        else:
                            print('Getting file content from corpus.')
                            file_content = self.sorted_corpus[self.list_fileview.currentRow()]['content']

                        print('Copying file to clipboard.')
                        pyperclip.copy(file_content)

                        print('Increasing copy count.')
                        self.sorted_corpus[self.list_fileview.currentRow()]['copy_count'] += 1
                        print(f'Copy count of file now: '
                              f'{self.sorted_corpus[self.list_fileview.currentRow()]["copy_count"]}')

                        if self.flag_preview_edited:
                            self.statusbar.showMessage('Temporary edits detected, preview content copied to clipboard')
                        else:
                            self.statusbar.showMessage('Copied file content to clipboard')

                except Exception as e:
                    print(e)
            elif self.list_fileview.count() == 1:
                file_content = self.textEdit_preview.toPlainText()
                pyperclip.copy(file_content)
                self.statusbar.showMessage('Copied file content to clipboard')

    def filter_filelist_view(self):
        """Brute force search using the IN operator. Fast enough using an in-memory filelist based on testing with the
        roughly expected number of files (hundreds)."""

        print('\nEntering filter_filelist_view function...')

        print(self.corpus[0])

        if self.lineEdit_search_by_text.text() == '' and self.radio_search_most_used.isChecked():
            self.list_fileview.clear()
            self.list_fileview.addItems(self.full_filelist_sorted)
        elif self.lineEdit_search_by_text.text() == '':
            self.list_fileview.clear()
            self.list_fileview.addItems(self.full_filelist)
        else:
            query = self.lineEdit_search_by_text.text().split()
            # if self.radio_search_most_used.isChecked():
            #     if case_sensitivity is True:
            #         self.filtered_corpus = [item for item in self.corpus
            #                                 if all(token in item['title'] for token in query)]
            #                                 # and item['copy_count'] > 0]
            #         self.filtered_corpus.sort(key=lambda x: x['copy_count'], reverse=True)
            #     elif case_sensitivity is False:
            #         self.filtered_corpus = [item for item in self.corpus
            #                                 if all(token.lower() in item['title'].lower() for token in query)]
            #                                 # and item['copy_count'] > 0]
            #         self.filtered_corpus.sort(key=lambda x: x['copy_count'], reverse=True)
            if self.combobox_search_by.currentText() == 'Filename':
                if case_sensitivity is True:
                    self.filtered_corpus = [item for item in self.corpus
                                            if all(token in item['title'] for token in query)]
                elif case_sensitivity is False:
                    self.filtered_corpus = [item for item in self.corpus
                                            if all(token.lower() in item['title'].lower() for token in query)]
            elif self.combobox_search_by.currentText() == 'File Contents':  # TODO: no self.file_contents any more??
                if case_sensitivity is True:
                    self.filtered_corpus = [self.corpus[k] for k, content in enumerate(self.file_contents)
                                            if all(token in content for token in query)]
                if case_sensitivity is False:
                    self.filtered_corpus = [self.corpus[k] for k, content in enumerate(self.file_contents)
                                            if all(token.lower() in content.lower() for token in query)]

            self.filtered_filelist_names = [item['title'] for item in self.filtered_corpus]
            self.list_fileview.clear()
            self.list_fileview.addItems(self.filtered_filelist_names)

        print('Finished running filter_filelist_view.')

    def browse_for_folder(self):  # simple dialogue direct from button, no custom widgets needed
        print('\nEntering browse_for_folder function...')
        folder_name = QFileDialog.getExistingDirectory(caption='Select directory')
        if folder_name:
            self.root_path.setText(folder_name)
            self.set_filelist()
            get_data(self.model, self.files[1])

    def closeEvent(self, event):
        # TODO: implement repickling ONLY if files updated through app during session
        #  see comment in update_file method
        # TODO: pickle position/size + app options
        print('\nEntering closeEvent function...')
        if self.flag_force_quit or not self.flag_minimise_to_tray:
            print('Force quitting or exiting + minimise_to_tray is False.')
            with open(pickle_file, 'wb') as pkl:
                pickle.dump(self.corpus, pkl)
                print('Dumped corpus to pickle file prior to exit.')
            self.close()
        elif self.flag_minimise_to_tray:
            event.ignore()
            self.hide()

    def force_quit(self):
        """Quitting from system tray will exit regardless of state."""
        print('\nEntering force_quit function...')
        print('Quit used from systray, setting force_quit_flag to True.')
        self.flag_force_quit = True
        self.close()

    # def bm25_filter_filelist_view(self):
    #     """Not getting the expected results, and I now think that the basic search using IN will likely be fast enough
    #     My guess is that the index is not getting built right, but not sure.
    #     """
    #     print('\n\nRunning filter_filelist function.')
    #     print(self.search_by_text_lineEdit.text())
    #     if self.search_by_text_lineEdit.text() == '':
    #         self.file_list_view.clear()
    #         self.file_list_view.addItems(self.filelist)
    #     else:
    #         if self.search_by_dropdown.currentText() == 'Filename':
    #             file_scores = self.get_scores(self.search_by_text_lineEdit.text().lower(), self.bm25_filenames)
    #             pprint(file_scores)
    #             filtered_list = [v for k, v in enumerate(self.filelist) if file_scores[k] > 0]
    #             pprint(filtered_list)
    #             self.file_list_view.clear()
    #             self.file_list_view.addItems(filtered_list)
    #         elif self.search_by_dropdown.currentText() == 'File Contents':
    #             file_scores = self.get_scores(self.search_by_text_lineEdit.text().lower(), self.bm25_filecontents)
    #             filtered_list = [v for k, v in enumerate(self.filelist) if file_scores[k] > 0]
    #             self.file_list_view.clear()
    #             self.file_list_view.addItems(filtered_list)

    # @staticmethod
    # def get_filelist(root, subdirs=search_subdirectories):
    #     """Gets a master list of files with full paths.
    #     Each element of the list is a dict as below:
    #     {'file': 'filename', 'full_path': '/full/path/to/file.txt'}
    #     """
    #     master_index = 0
    #
    #     def process_folder(files_in_folder, result_list, current_path):
    #         """Process a single folder. This function is to avoid repeating code."""
    #         nonlocal master_index
    #         for file in files_in_folder:
    #             result_list.append({'file': file,
    #                                 'full_path': os.path.join(current_path, file),
    #                                 'index': master_index
    #                                 })
    #             master_index += 1
    #
    #     print('Running get_filelist function.')
    #     file_list = []
    #     if subdirs:
    #         for path, subdirs, files in os.walk(top=root):
    #             process_folder(files, result_list=file_list, current_path=path)
    #     else:
    #         files = os.listdir(root)
    #         process_folder(files, result_list=file_list, current_path=root)
    #     # names = [x['file'].split('.')[0] for x in file_list]
    #     # print(f'File_list: {file_list}')
    #     return file_list

    # @staticmethod
    # def get_scores(query, bm25_index):
    #     tokenised_query = query.split(' ')
    #     _item_scores = bm25_index.get_scores(tokenised_query)
    #     return _item_scores

    # @staticmethod
    # def index_data_source(root, subdirs=True, inclusions=None, exclusions=None):
    #     """
    #     Currently only supports file-system indexing.
    #     :param root: root folder
    #     :param subdirs: bool, traverse subdirs or not
    #     :param inclusions: exclusive list of folders to look in, all other folders will be ignored, defaults to None
    #     :param exclusions: exclusive list of folders to ignore, all files and subdirectories within each folder will
    #     be ignored, defaults to None
    #     :return: returns a dictionary representing all keywords found in files
    #     """
    #
    #     def get_words(doc_content):
    #         replace_dict = {'\n': ' ',
    #                         ',': '',
    #                         '.  ': '',
    #                         '  ': ' ',
    #                         '"': '',
    #                         # '.': '',  # removing this to allow for searching stuff like 'sys.databases'
    #                         '(': ' ',
    #                         ')': ' ',
    #                         '{': ' ',
    #                         '}': ' ',
    #                         '\\': '',
    #                         '[': '',
    #                         ']': '',
    #                         # '_': '',  # removing this to allow for searching variables with underscores
    #                         '^': '',
    #                         '=': ' '
    #                         }
    #         res = ''.join(idx if idx not in replace_dict else replace_dict[idx] for idx in doc_content)
    #         words_ = res.split(sep=' ')
    #         words_ = [word_ for word_ in words_ if word_ != '']
    #         return words_
    #
    #     indexed = {}
    #     if subdirs:
    #         for path, subdirs, files in os.walk(top=root):
    #             for filename in files:
    #                 with open(os.path.join(path, filename), 'r', encoding='UTF-8') as f:
    #                     try:
    #                         content = f.read()
    #                     except Exception as e:
    #                         print(f, e)
    #                     words = get_words(content)
    #                     unique_words = set(words)
    #                     for word in unique_words:
    #                         if word in indexed.keys():
    #                             indexed[word].append(filename)
    #                         else:
    #                             indexed[word] = [filename]
    #     else:
    #         for file in os.listdir(root):
    #             with open(root + file, 'r') as f:
    #                 content = f.read()
    #                 words = get_words(content)
    #                 unique_words = set(words)
    #                 for word in unique_words:
    #                     if word in indexed.keys():
    #                         indexed[word].append(file)
    #                     else:
    #                         indexed[word] = [file]
    #     return indexed
# class NewFile(QWidget):
#     """Floating window to create a new file."""
#     def __init__(self):
#         super().__init__()
#         # new file layout
#         self.new_file_layout = QVBoxLayout()
#         # new file sections
#         self.folder_select_layout = QHBoxLayout()
#         self.filename_layout = QHBoxLayout()
#         self.text_edit_layout = QVBoxLayout()
#
#         # add children to new_file_layout
#         self.new_file_layout.addLayout(self.folder_select_layout)
#         self.new_file_layout.addLayout(self.filename_layout)
#         self.new_file_layout.addLayout(self.text_edit_layout)
#
#         # specify widgets
#         self.select_folder_widget = QFileDialog()
#         self.select_folder_button = QPushButton(text='Select Folder')
#         # self.select_folder_button.clicked.connect(self.select_folder_dialogue)
#         self.input_filename_widget = QLineEdit()
#         self.input_filecontent_widget = QTextEdit()
#         self.save_file_button = QPushButton(text='Save New File')
#         # self.save_file_button.clicked.connect(self.save_new_file)
#
#         # add widgets to layouts
#         self.folder_select_layout.addWidget(self.select_folder_widget)
#         self.folder_select_layout.addWidget(self.select_folder_button)
#         self.filename_layout.addWidget(self.input_filename_widget)
#         self.text_edit_layout.addWidget(self.input_filecontent_widget)
#         self.new_file_layout.addWidget(self.save_file_button)
#
#         self.show()
#         pass


def run():
    # noinspection PyArgumentList

    app = QApplication(sys.argv)

    window = MainWindow()
    window.setWindowFlags(Qt.WindowStaysOnTopHint)
    window.setMinimumWidth(200)
    window.show()
    app.exec_()


if __name__ == '__main__':
    run()
