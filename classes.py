from pathlib import Path
from datetime import datetime
import spacy
import re
import os

# load nlp, used in get_corpus method
nlp = spacy.load('en_core_web_sm')
nlp.disable_pipes(['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'ner', 'lemmatizer'])


class Config:
    """Defines the configuration options for the GUI. To be serialised on quitting the app, and loaded/re-initialised
    on app start.
    This is separate to permanent configuration options like the app icon etc."""
    def __init__(self
                 , first_time_user=False
                 , case_sensitive_search=True
                 , display_filename_suffixes=True
                 , window_x=400
                 , window_y=400
                 , window_width=200
                 , window_height=300):
        self.first_time_user = first_time_user
        self.case_sensitive_search = case_sensitive_search
        self.display_filename_suffixes = display_filename_suffixes
        self.window_x = window_x
        self.window_y = window_y
        self.window_width = window_width
        self.window_height = window_height


class Source:
    """Defines a source for documents. Intended to be a generic class to allow for further document systems to be
    supported later. Stand-alone object, to be held in a list in the corpus.

    Location: Holds the root location for finding files.
    Credentials: Any credentials/references to credentials if necessary.
    Subdirectories: Whether to search subdirectories recursively or not.
    Exclude_folders: An exclusive list of folders to ignore when traversing the source.
    Include_folders: An exclusive list of folders to include when traversing the source, ignoring all other folders.

    Could implement a method to get/provide it's referenced credentials later. These may be references to the specific
    API's of different document systems.
    """
    def __init__(self
                 , kind: str
                 , root: str
                 , credentials=None
                 , subdirectories: bool=True
                 , exclude_folders: list=None
                 , include_folders: list=None):
        self.kind = kind
        self.root = root
        self.credentials = credentials
        self.subdirectories = subdirectories
        self.exclude_folders = exclude_folders
        self.include_folders = include_folders


class Document:
    """Generic parent class with the common attributes/methods shared by all types of documents.
    Sub-classes for specific types of documents will be created as needed with specific attributes/methods that apply
    to that type.

    For the last_modified arg, this will either take a datetime or float. It will implicitly convert a float to a
    datetime as part of instantiation.

    A document is responsible for defining it's type (Windows file, etc) and it's source (full path, url, etc).
    (The Browser class is responsible for getting updates to the file from the source.)
    (Another thought, the document could just hold it's relative path from the root/source, with the source class
    holding the absolute 'path'/url from which to start, along with any necessary creds etc.)

    Only supporting Windows at the moment.

    Data subsystems that could be supported in future:
        - Linux filesystem (different version)
        - Mac filesystem (different version)
        - Dropbox
        - Google Drive
        - OneDrive
        - GitHub?
        - Confluence?
        - Sharepoint?
        - IDrive?
        - SpiderOak?
        - pCloud?
        - IceDrive?
        - NordLocker?
        - Backblaze?
        - see list of more here at bottom of page: https://www.techradar.com/nz/news/the-best-cloud-storage
    """
    def __init__(self
                 , uid: int = None
                 , title: str = None
                 , content: str = None
                 , source: Source = None
                 , full_path: str = None
                 , last_modified: float = None
                 , copy_count: int = None
                 ):
        """
        :type uid: int
        :type title: str
        :type content: str
        :type source: Source
        :type full_path: str
        :type last_modified: datetime
        :type copy_count: int
        """
        self.uid = uid
        self.title = title
        self.content = content
        self.source = source
        self.full_path = full_path
        self.last_modified = last_modified
        self.copy_count = copy_count

    def __repr__(self):
        return f'Document - UID: {self.uid}, Title: {self.title}'

    @property
    def parent_folder(self):
        folder_path = Path(self.full_path)
        return folder_path.parts[-2]

    @property
    def title_tokens(self):
        name = self.title.split('.')[0]
        string = nlp(name)
        tokens = set([token.text.lower() for token in string if token.is_alpha])
        return tokens

    @property
    def content_tokens(self):
        string = nlp(self.content)
        tokens = set([token.text.lower() for token in string if token.is_alpha])
        return tokens

    # @property
    # def readable_datetime(self):
    #     return self.last_modified.strftime('%Y-%m-%d %H:%M:%S')


class Corpus:
    """Holds the list of sources, list of documents, and controls the distribution of unique id's to documents.

    """
    def __init__(self
                 , sources: list = None
                 , documents: list = None
                 , next_id: int = 0):
        """
        :type sources: object
        :type documents: object
        :type next_id: object
        """
        self.sources = sources
        self.documents = documents
        self.next_id = next_id

    def give_next_id(self, doc: Document):
        """Sets the UID for the provided document, this is called implicitly when a document is added to the corpus, so
        care is needed if calling it manually. This function may be placed inside the add_document() function in the
        future, to avoid confusion."""
        doc.uid = self.next_id
        self.next_id += 1

    def add_document(self, document: Document):
        """Adds the given document to the corpus. Calls give_next_id() to assign an appropriate UID to the document."""
        self.give_next_id(document)
        self.documents.append(document)

    def check_for_updates(self):
        print("Currently points to placeholder function in Browser class.")
        browser = Browser()
        for document in self.documents:
            browser.check_for_document_update(document)


class Browser:
    """The Browser is responsible for getting files and updates to files. It has no attributes and is a
    convenience class for accessing browsing related methods.

    This may not even be directly used, I think the Document/Corpus classes may be the entry points."""

    @staticmethod
    def get_source_documents(source, corpus: Corpus):
        """Get all files from a source the first time, or if the saved corpus is deleted.
        This is run iteratively on the defined sources, with each document being added to the corpus at some point,
        although this may be handled by the Corpus class.

        If corpus is None, it is assumed that this is the first source, so a new corpus will need to be initialised. In
        other cases, a pre-initialised/built corpus should be provided for this arg. In the case of a pre-built corpus,
        the list of sources should be checked to ensure this new source does not match a pre-existing one.
        All files still need to be checked against pre-existing documents, as a given source may be a parent to a
        pre-existing source.

        It is assumed that a recursive search is desired.
        """
        _corpus = corpus

        # assuming a Windows filesystem for the time-being
        for path, subdirs, files in os.walk(top=source.root):
            # calculate this list comprehension once and then refer to it below
            if _corpus.documents is None:
                _corpus.documents = []
            current_paths = [document.full_path for document in _corpus.documents]
            for filename in files:
                # check full-path doesn't already exist in corpus docs
                if os.path.join(path, filename) not in current_paths:
                    # get document attr's
                    try:
                        with open(os.path.join(path, filename), 'r', encoding='UTF-8') as f:
                            content = f.read()
                    except Exception as e:
                        print(e)
                    title = filename
                    full_path = os.path.join(path, filename)
                    last_mod_date = os.path.getmtime(path)

                    document = Document(title=title
                                        , content=content
                                        , source=source
                                        , full_path=full_path
                                        , last_modified=last_mod_date
                                        , copy_count=0)

                    _corpus.add_document(document)
                else:
                    print(f'Document ({filename}) at location {path}, already exists within the corpus, skipping.')

    def check_for_document_update(self, document: Document):
        """Check for update to a given document. Documents are responsible for knowing their source location and kind,
        hence only the document needs to be passed in and the rest is taken care of.

        This is run iteratively on each of the documents in a corpus when checking for updates on first load.
        """
        pass

    def update_source_document(self, document: Document):
        """On attempting an update of the local corpus copy of the document, this is called to attempt to update the
        source document.

        Notes:
            - if update of source document fails, then the update should be held in the corpus, along with the attempted
            update datetime, then when updates are checked the source file's 'last modified' time will be behind, which
            could trigger another attempted update.
            - if update of source fails, should display a message to the user saying why it failed and potentially offer
            a remedy, such as re-authenticating for online sources etc.
        """
        pass
