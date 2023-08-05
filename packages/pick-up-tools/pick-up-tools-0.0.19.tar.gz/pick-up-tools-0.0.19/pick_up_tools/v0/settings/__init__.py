import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
relative = lambda *args: os.path.join(*args)


class Settings(object):
    def __init__(self, current_path=__file__):
        self._base_dir = Path(current_path).resolve().parent.parent

    @property
    def BASE_DIR(self):
        return self._base_dir
