import os
import document
import corpus


# later import libraries for browsing web


class Browser:
    """The Browser is responsible for getting files and updates to files. It has no attributes and is a
    convenience class for accessing browsing related methods.

    This may not even be directly used, I think the Document/Corpus classes may be the entry points."""

    @staticmethod
    def get_source_documents(source, corpus: corpus.Corpus = None):
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
        if not source:
            return print('Source not set, exiting')

        else:
            if corpus is None:  # init new corpus
                _corpus = Corpus()
            else:
                _corpus = corpus

            # assuming a Windows filesystem for the time-being
            for path, subdirs, files in os.walk(top=source.root):
                # calculate this list comprehension once and then refer to it below
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
