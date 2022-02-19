class Source:
    """
    Location: Holds the root location for finding files.
    Credentials: Any credentials/references to credentials if necessary.
    Subdirectories: Whether to search subdirectories recursively or not.
    Exclude_folders: An exclusive list of folders to ignore when traversing the source.
    Include_folders: An exclusive list of folders to include when traversing the source, ignoring all other folders.
    """
    def __init__(self
                 , root: str
                 , credentials=None
                 , subdirectories: bool = True
                 , exclude_folders: list = None
                 , include_folders: list = None):
        self.root = root
        self.credentials = credentials
        self.subdirectories = subdirectories
        self.exclude_folders = exclude_folders
        self.include_folders = include_folders
