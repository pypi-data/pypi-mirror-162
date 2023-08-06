import os

ESSENTIAL_DATA_IDENTIFIER = "1xuHxiyj8t5qReYMN8P-bDLG0X7lpBHip"
"Google Drive File ID of essential data zip archive for this project"

ESSENTIAL_DATA_ARCHIVE_NAME = os.path.normpath(os.path.dirname(__file__) + "/../data/scistag_essentials.zip")
"Local file name of essential data"

ESSENTIAL_DATA_PATH = "localzip://@scistagessential/"