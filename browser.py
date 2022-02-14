import os
from document import Document
# later import libraries for browsing web


class Browser:
    """The Browser is responsible for getting files and updates to files. It has no attributes and is a
    convenience class for accessing browsing related methods.

    This may not even be directly used, I think the Document/Corpus classes may be the entry points."""

    def get_source_documents(self, source, subdirectories=False):
        """Get all files from a source the first time, or if the saved corpus is deleted.
        This is run iteratively on the defined sources, with each document being added to the corpus at some point,
        although this may be handled by the Corpus class.
        """
        pass

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
