import io
import zipfile
from multiprocessing import RLock
from typing import Union, Optional, List
import fnmatch

ZIP_SOURCE_PROTOCOL = "localzip://"
"A file path flagging the file as being stored in a zipfile"


class SharedArchive:
    """
    Defines a shared zip archive which can be used by multiple users, e.g. classes to provide shared data quickly from a
    compact archive once initialized.

    Usage:
    SharedArchive.register("sharedData.zip", "sharedData")

    Then data can be loaded flexible via FileStag, independent of if it's located in the web, in a zip archive or
    as simple local file:
    FileStag.load_file("localzip://@sharedData/testFile.zip")
    FileStag.load_file("local_file.txt")
    FileStag.load_file("http://www....")

    Note: Registered zip files have to add an @ in front of their identifier.
    """

    access_lock = RLock()
    archives = {}

    def __init__(self, source: Union[str, bytes], identifier: str, cache=False):
        """
        Initializer
        :param source: The source, either a filename or a bytes object
        :param identifier: The identifier via which this object can be accessed
        :param cache: Defines if this archive shall be cached in memory
        """
        self.identifier = identifier
        self.access_lock = RLock()
        if isinstance(source, str) and cache:
            source = io.BytesIO(open(source, "rb").read())
        elif isinstance(source, bytes):
            source = io.BytesIO(source)
        self.zip_file = zipfile.ZipFile(source)

    def find_files(self, name_filter: str = "*") -> List[str]:
        """
        Lists all element from the archive matching given filter
        :param name_filter: The filter
        :return: The list of found elements
        """
        with self.access_lock:
            elements = [element.filename for element in self.zip_file.filelist if
                        fnmatch.fnmatch(element.filename, name_filter)]
            return elements

    def exists(self, name: str) -> bool:
        """
        Returns if the file exists
        :param name: The file's name
        :return: True if it exists
        """
        with self.access_lock:
            return name in self.zip_file.namelist()

    def read_file(self, name: str) -> Optional[bytes]:
        """
        Loads the data from given file to memory
        :param name: The name of the file to load
        :return: The file's data. None if the file could not be found
        """
        with self.access_lock:
            if name not in self.zip_file.namelist():
                return None
            return self.zip_file.open(name, "r").read()

    @classmethod
    def register(cls, source: Union[str, bytes], identifier: str, cache=False) -> "SharedArchive":
        """
        Registers a new archive.
        :param source: The source, either a filename or a bytes object
        :param identifier: The identifier via which this object can be accessed
        :param cache: Defines if this archive shall be cached in memory
        :return: The archive
        """
        assert len(identifier)
        with cls.access_lock:
            if identifier in cls.archives:
                return cls.archives[identifier]
            new_archive = SharedArchive(source, identifier, cache)
            cls.archives[identifier] = new_archive
            return new_archive

    @classmethod
    def verify_file(cls, identifier: str, filename: Optional[str] = None) -> bool:
        """
        Returns if given file exists
        :param identifier: The archive identifier. Alternate: a full identifier in the form
        localzip://@identifier/filename
        :param filename: The name of the file to load.
        :return: True if the file exists
        """
        archive: Optional[None] = None
        if identifier.startswith(ZIP_SOURCE_PROTOCOL):
            identifier = identifier[len(ZIP_SOURCE_PROTOCOL):]
            if not identifier.startswith("@"):
                raise ValueError("Missing @ sign at the beginning of zip file identifier")
            if "/" not in identifier:
                raise ValueError("No filename provided. Form: localzip://@identifier/filename")
            slash_index = identifier.index("/")
            filename = identifier[slash_index + 1:]
            identifier = identifier[1:slash_index]
        with cls.access_lock:
            if identifier in cls.archives:
                archive = cls.archives[identifier]
        if archive is None:
            return False
        archive: SharedArchive
        return archive.exists(filename)

    @classmethod
    def load_file(cls, identifier: str, filename: Optional[str] = None) -> Optional[bytes]:
        """
        Loads a file by filename
        :param identifier: The archive identifier. Alternate: a full identifier in the form
        localzip://@identifier/filename
        :param filename: The name of the file to load.
        :return: The data if the file could be found
        """
        archive: Optional[None] = None
        if identifier.startswith(ZIP_SOURCE_PROTOCOL):
            identifier = identifier[len(ZIP_SOURCE_PROTOCOL):]
            if not identifier.startswith("@"):
                raise ValueError("Missing @ sign at the beginning of zip file identifier")
            if "/" not in identifier:
                raise ValueError("No filename provided. Form: localzip://@identifier/filename")
            slash_index = identifier.index("/")
            filename = identifier[slash_index + 1:]
            identifier = identifier[1:slash_index]
        with cls.access_lock:
            if identifier in cls.archives:
                archive = cls.archives[identifier]
        if archive is None:
            return None
        archive: SharedArchive
        return archive.read_file(filename)

    @classmethod
    def scan(cls, identifier: str, name_filter: str = "*", long_identifier=True) -> List[str]:
        """
        Scans the archive for given file mask
        :param identifier: The archive identifier
        :param name_filter: The name mask to search for
        :param long_identifier: Defines if the scan shall return long identifiers
        (localzip://@identifier/filename) so the results can be used for FileStag.load_file). True by default.
        :return: All file in given archive matching the mask
        """
        archive: Optional[None] = None
        with cls.access_lock:
            if identifier in cls.archives:
                archive = cls.archives[identifier]
        if archive is None:
            return []
        archive: SharedArchive
        results = archive.find_files(name_filter)
        if long_identifier:
            results = [f"{ZIP_SOURCE_PROTOCOL}@{identifier}/{element}" for element in results]
        return results


__all__ = [SharedArchive, ZIP_SOURCE_PROTOCOL]
