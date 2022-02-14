from document import Document
"""Class module for the Corpus.

Notes:
    - the corpus will be responsible for handling the giving of UID's to documents to ensure unique records and allow
    for easier referencing to documents during calls for title/content/source etc.
    I think this will most easily be handled by a class attribute called 'next_id', so when a document is added I can
    call something like 'give_next_id()'.
"""


class Corpus:
    """Holds the list of sources, list of documents, and controls the distribution of unique id's to documents.

    """
    def __init__(self,
                 sources: list,
                 documents: list,
                 next_id: int = 0):
        """

        :type sources: object
        :type documents: object
        :type next_id: object
        """
        self.sources = sources
        self.documents = documents
        self.next_id = next_id

    def give_next_id(self, document: Document):
        document.uid = self.next_id
        self.next_id += 1
