import tarfile
import zipfile
from pathlib import Path


def extract_all(path: str, to: str = None):
    """Extract archive file.

    Parameters
    ----------
    path: str
        Path of archive file to be extracted.
    to: str, optional
        Directory to which the archive file will be extracted.
        If None, it will be set to the parent directory of the archive file.
    """
    path = Path(path)
    to = Path(to) if to else path.parent

    if path.suffix == ".zip":
        opener, mode = zipfile.ZipFile, "r"
    elif path.suffix == ".tar":
        opener, mode = tarfile.open, "r"
    elif path.suffixes[-2:] in [(".tar", ".gz"), (".tgz",)]:
        opener, mode = tarfile.open, "r:gz"
    elif path.suffixes[-2:] in [(".tar", ".bz2"), (".tbz",)]:
        opener, mode = tarfile.open, "r:bz2"
    else:
        raise ValueError(
            f"Could not extract '{path}' as no appropriate extractor is found"
        )

    def namelist(f):
        if isinstance(f, zipfile.ZipFile):
            return f.namelist()
        return [m.name for m in f.getmembers()]

    def filelist(f):
        return [str(to / fname) for fname in namelist(f)]

    with opener(path, mode) as f:
        f.extractall(path=to)

    return filelist(f)
