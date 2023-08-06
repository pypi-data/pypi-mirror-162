import os


def is_windows():
    return os.name == "nt"


def fix_lims_path(path):
    if path.startswith("/allen"):
        return "/" + path

    return path
