"""
A file contains all constant values
"""

MAX_NUMBER_FILES = 50

CHUNK_SIZE = 512 * 1024  # 512KB


PARSING_PATTERNS = [
    r"^/file/d/(.*?)/(edit|view)$",
    r"^/file/u/[0-9]+/d/(.*?)/(edit|view)$",
    r"^/document/d/(.*?)/(edit|htmlview|view)$",
    r"^/document/u/[0-9]+/d/(.*?)/(edit|htmlview|view)$",
    r"^/presentation/d/(.*?)/(edit|htmlview|view)$",
    r"^/presentation/u/[0-9]+/d/(.*?)/(edit|htmlview|view)$",
    r"^/spreadsheets/d/(.*?)/(edit|htmlview|view)$",
    r"^/spreadsheets/u/[0-9]+/d/(.*?)/(edit|htmlview|view)$",
]


USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
