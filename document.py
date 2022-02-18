from pathlib import Path
from datetime import datetime
import re
from source import Source


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
                 , last_modified: datetime = None
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
        if type(self.last_modified) is datetime:
            self.last_modified = last_modified
        elif type(self.last_modified) is float:
            self.last_modified = datetime.fromtimestamp(self.last_modified)
        else:
            print('\n\nWarning, data type of last_modified arg was not float or datetime.')
            self.last_modified = last_modified
        self.copy_count = copy_count

    def __repr__(self):
        print(
            f'Document -'
            f' UID: {self.uid}'
            f' Title: {self.title}'
        )

    # @property
    # def full_path(self):
    #     path = Path(self.source)
    #     return path.joinpath(self.title)

    @property
    def parent_folder(self):
        folder_path = Path(self.source)
        return folder_path.parts[-2]

    @property
    def title_tokens(self):
        return re.findall(r'\b\w+\b', self.title)

    @property
    def content_tokens(self):
        return re.findall(r'\b\w+\b', self.content)

    @property
    def readable_datetime(self):
        return self.last_modified.strftime('%Y-%m-%d %H:%M:%S')
