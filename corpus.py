from document import Document
from browser import Browser
"""Class module for the Corpus.

Notes:
    - the corpus will be responsible for handling the giving of UID's to documents to ensure unique records and allow
    for easier referencing to documents during calls for title/content/source etc.
"""


class Corpus:
    """Holds the list of sources, list of documents, and controls the distribution of unique id's to documents.

    """
    def __init__(self,
                 sources: list = None,
                 documents: list = None,
                 next_id: int = 0):
        """

        :type sources: object
        :type documents: object
        :type next_id: object
        """
        self.sources = sources
        self.documents = documents
        self.next_id = next_id

    def give_next_id(self, document: Document=None):
        """If given a document, will set the document uid, else will return the uid to be given to the document."""
        document.uid = self.next_id
        self.next_id += 1

    def add_document(self, document):
        self.give_next_id(document)
        self.documents.append(document)

    def check_for_updates(self):
        print("Currently points to placeholder function in Browser class.")
        browser = Browser()
        for document in self.documents:
            browser.check_for_document_update(document)
