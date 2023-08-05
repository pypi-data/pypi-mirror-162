import os
import platform
from glob import glob

import pandas as pd
from tqdm import tqdm


class FileType(object):
    def __init__(self, path: str, encoding: str = 'utf-8', sheet_name='Sheet1'):
        self.path = path
        self.encoding = encoding
        self.sheet_name = sheet_name

    def exists(self):
        return os.path.exists(self.path)

    def get(self, **kwargs):
        return None

    def load(self, **kwargs):
        return self.get(**kwargs) if self.exists() else None


class Json(FileType):
    def get(self, **kwargs):
        orient = kwargs.get('orient', 'records')
        return pd.read_json(self.path, encoding=self.encoding, orient=orient)

    def save(self, df, **kwargs):
        orient = kwargs.get('orient', 'records')
        index = kwargs.get('index', False)
        if orient in ['split', 'table']:
            df.to_json(self.path, orient=orient, index=index)
        else:
            df.to_json(self.path, orient=orient)


class Csv(FileType):
    def get(self, **kwargs):
        return pd.read_csv(self.path, encoding=self.encoding)

    def save(self, df, **kwargs):
        index = kwargs.get('index', False)
        df.to_csv(self.path, encoding=self.encoding, index=index)


class Xlsx(FileType):
    def get(self, **kwargs):
        return pd.read_excel(self.path, sheet_name=self.sheet_name)

    def save(self, df, **kwargs):
        index = kwargs.get('index', False)
        df.to_excel(self.path, encoding=self.encoding, sheet_name=self.sheet_name, index=index)


class Xls(FileType):
    def get(self, **kwargs):
        return pd.read_excel(self.path, sheet_name=self.sheet_name, )

    def save(self, df, **kwargs):
        index = kwargs.get('index', False)
        df.to_excel(self.path, encoding=self.encoding, sheet_name=self.sheet_name, index=index)


class FileManager(object):
    def __init__(self, path: str, encoding: str = 'utf-8', sheet_name='Sheet1'):
        self._path = path
        self._encoding = encoding
        self._sheet_name = sheet_name

    def json(self):
        _ins = Json(path=self._path, encoding=self._encoding)
        return _ins

    def csv(self):
        _ins = Csv(path=self._path, encoding=self._encoding)
        return _ins

    def xlsx(self):
        _ins = Xlsx(path=self._path, encoding=self._encoding, sheet_name=self._sheet_name)
        return _ins

    def xls(self):
        _ins = Xls(path=self._path, encoding=self._encoding, sheet_name=self._sheet_name)
        return _ins

    def load(self, **kwargs) -> pd.DataFrame:
        file_type = self._path.split('.')[-1]
        return eval(f'self.{file_type}().load(**kwargs)')

    def save(self, **kwargs) -> pd.DataFrame:
        file_type = self._path.split('.')[-1]
        return eval(f'self.{file_type}().save(**kwargs)')


class LocalFile(object):
    def __init__(self, path: str, encoding: str = 'utf-8', sheet_name='Sheet1'):
        self.path = path
        self.file = FileManager(path=path, encoding=encoding, sheet_name=sheet_name)
        self._data = None

    def write(self, data: pd.DataFrame, **kwargs):
        self.file.save(df=data, **kwargs)

    def read(self, **kwargs):
        return self.file.load(**kwargs)

    def delete(self):
        if self.exist:
            os.remove(self.path)
            return True
        return False

    @property
    def exist(self):
        return os.path.exists(self.path)


class LocalListFiles(object):
    def __init__(self, path, recursive=True, encoding: str = 'utf-8', sheet_name='Sheet1'):
        self.path = path
        self.recursive = recursive
        self.encoding = encoding
        self.sheet_name = sheet_name

    @property
    def files(self):
        _files = glob(self.path, recursive=self.recursive)
        if platform.system().lower() == 'windows':
            _files = [i.replace('\\', '/') for i in _files]
        files = [LocalFile(path=path, encoding=self.encoding, sheet_name=self.sheet_name) for path in _files]
        return files

    def read(self, **kwargs):
        for file in self.files:
            yield file.read(**kwargs)

    def delete(self):
        flag = True
        for file in tqdm(self.files, desc='delete files'):
            flag &= file.delete()
        return flag
