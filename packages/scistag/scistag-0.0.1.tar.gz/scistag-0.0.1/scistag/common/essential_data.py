import os
from scistag.common.configuration import ESSENTIAL_DATA_IDENTIFIER, ESSENTIAL_DATA_ARCHIVE_NAME, ESSENTIAL_DATA_PATH


def prepare_essential_data() -> bool:
    """
    Downloads the essential data required for SciStag from the web
    :return: True on success
    """
    from scistag.filestag import SharedArchive
    path = ESSENTIAL_DATA_ARCHIVE_NAME
    if not os.path.exists(path):
        import gdown
        gdown.download(id=ESSENTIAL_DATA_IDENTIFIER, output=path, quiet=False)
    SharedArchive.register(ESSENTIAL_DATA_ARCHIVE_NAME, "scistagessential", cache=False)
    return os.path.exists(path)


prepare_essential_data()
