import os

from .dirutils import joiner
from .utils import env_get

curdir = os.path.dirname(__file__)
schnelldir_byrelative = os.path.join(curdir, "..")
sidoarjodir = os.path.join(curdir, "../..")
datadir = env_get("ULIBPY_DATA_FOLDER_ABS", os.path.join(sidoarjodir, "data"))


def datadir_():
    return env_get("ULIBPY_DATA_FOLDER_ABS")


def datadir0():
    return joiner(sidoarjo(), "data")


def github_token():
    return env_get("ULIBPY_GITHUB_TOKEN")


def schnelldir():
    return env_get("ULIBPY_BASEDIR", schnelldir_byrelative)


def sidoarjo():
    return env_get("ULIBPY_ROOTDIR")


def bylangsdir():
    return env_get("ULIBPY_BYLANGSDIR")


def databasedir():
    return joiner(sidoarjo(), "database")


def debuglevel():
    return env_get("ULIBPY_FMUS_DEBUG")


def default_entry():
    # utk repl:1055
    return env_get("ULIBPY_MKFILE_KEY")


def dirjoiner(*daftar):
    """
    filepath = dirjoiner(schnelldir(), 'gui/system/help/README.md')
    perintah_shell(f'code {filepath}')
    """
    return joiner(*daftar)
