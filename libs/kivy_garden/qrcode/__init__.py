"""
Exposes `QRCodeWidget`.
Note this may break `pip` since all imports within `qrcode_widget.py` would be
required at setup time. This is because `version.py` (same directory) is used
by the `setup.py` file.
Hence we're not exposing `QRCodeWidget` if `pip` is detected.
"""
import os

project_dir = os.path.abspath(
    os.path.join(__file__, os.pardir, os.pardir, os.pardir, os.pardir)
)
using_pip = os.path.basename(project_dir).startswith("pip-")
# only exposes `QRCodeWidget` if not within `pip` ongoing install
if not using_pip:
    from .qrcode_widget import QRCodeWidget  # noqa
