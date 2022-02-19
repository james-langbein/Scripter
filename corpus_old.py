import document_old
import browser_old


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

    def give_next_id(self, doc: document_old.Document):
        """Sets the UID for the provided document, this is called implicitly when a document is added to the corpus, so
        care is needed if calling it manually. This function may be placed inside the add_document() function in the
        future, to avoid confusion."""
        doc.uid = self.next_id
        self.next_id += 1

    def add_document(self, doc: document_old.Document):
        """Adds the given document to the corpus. Calls give_next_id() to assign an appropriate UID to the document."""
        self.give_next_id(doc)
        self.documents.append(doc)

    def check_for_updates(self):
        print("Currently points to placeholder function in Browser class.")
        browse = browser_old.Browser()
        for doc in self.documents:
            browse.check_for_document_update(doc)
