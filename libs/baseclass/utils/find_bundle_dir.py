import sys
from pathlib import Path


def find_bundle_dir(file):
    if getattr(sys, "frozen", False):
        # The application is frozen
        bundle_dir = Path(sys._MEIPASS)

    else:
        # The application is not frozen
        bundle_dir = Path(file).parent

        has_main_file = list(bundle_dir.glob("main.py"))
        while len(has_main_file) == 0 and len(bundle_dir.parents) != 0:
            bundle_dir = bundle_dir.parent
            has_main_file = list(bundle_dir.glob("main.py"))

    return bundle_dir
