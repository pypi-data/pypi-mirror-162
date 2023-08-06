import os
from scistag.gitstag import GitScanner


def test_repo_validity():
    scanner = GitScanner()
    scistag_base_path = os.path.normpath(os.path.dirname(__file__) + "/../../../")
    scanner.scan(scistag_base_path)
    # check the repo does not exceed a reasonable size and has a reasonable count of files and directories
    assert scanner.total_size < 1000000
    assert 195 < scanner.file_count < 220
    assert 109 < scanner.dir_count < 115
    lf_ignore_list = ["*/poetry.lock", "*/web/icons/Icon*", "*/AppIcon.appiconset/Icon*", "*/project.pbxproj",
                      "*/data_stag_connection.py", "*/data_stag_vault.py",
                      "*/imagestag/image.py", "*/slidestag/widget.py"]
    
    too_large_files = scanner.get_large_files(min_size=15000, hard_limit_size=100000, ignore_list=lf_ignore_list)
    assert len(too_large_files) == 0
