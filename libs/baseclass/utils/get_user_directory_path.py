import os

from kivy.utils import platform


def get_user_directory_path():
    if platform == "android":
        return os.getenv("EXTERNAL_STORAGE")

    return os.path.expanduser("~")
