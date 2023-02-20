import sys
from pathlib import Path


def get_working_dir(file):
    if getattr(sys, "frozen", False):
        # The application is frozen
        working_dir = Path(sys.executable).parent
    else:
        # The application is not frozen
        working_dir = Path(file).parent

        has_main_file = list(working_dir.glob("main.py"))
        while len(has_main_file) == 0 and len(working_dir.parents) != 0:
            working_dir = working_dir.parent
            has_main_file = list(working_dir.glob("main.py"))

    return working_dir
