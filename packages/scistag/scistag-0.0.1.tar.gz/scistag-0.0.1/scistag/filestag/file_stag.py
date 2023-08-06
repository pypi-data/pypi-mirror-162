import os
from typing import Optional, List

from scistag.webstag import web_fetch


class FileStag:
    """
    Helper class to load data from a variety of sources such as local files, registered archives of the web
    """

    @classmethod
    def load_file(cls, filename: str) -> Optional[bytes]:
        """
        Loads a file by filename from a local file, a registered web archive or the web
        :param filename: The filename or identifier. e.g.  localzip://@identifier/filename
        :return: The data if the file could be found
        """
        from .shared_archive import ZIP_SOURCE_PROTOCOL, SharedArchive
        if filename.startswith(ZIP_SOURCE_PROTOCOL):
            return SharedArchive.load_file(filename)
        elif filename.startswith("http://") or filename.startswith("https://"):
            return web_fetch(filename)
        else:
            if os.path.exists(filename):
                return open(filename, "rb").read()
            else:
                return None

    @classmethod
    def exists(cls, filename: str) -> bool:
        """
        Verifies if a file exists
        :param filename: The filename or identifier. e.g.  localzip://@identifier/filename
        :return: True if the file exists
        """
        from .shared_archive import ZIP_SOURCE_PROTOCOL, SharedArchive
        if filename.startswith(ZIP_SOURCE_PROTOCOL):
            return SharedArchive.verify_file(filename)
        elif filename.startswith("http://") or filename.startswith("https://"):
            return web_fetch(filename) is not None
        else:
            return os.path.exists(filename)
