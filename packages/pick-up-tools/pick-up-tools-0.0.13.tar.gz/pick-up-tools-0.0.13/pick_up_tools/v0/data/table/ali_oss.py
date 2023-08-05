import fnmatch
import oss2
from tqdm import tqdm


class OSS2(object):
    def __init__(self, access_id, access_secret, bucket, endpoint='https://oss-cn-hangzhou.aliyuncs.com'):
        auth = oss2.Auth(access_id, access_secret)
        self.bucket = oss2.Bucket(auth, endpoint=endpoint, bucket_name=bucket)

    def list_files(self, match='*', prefix='', delimiter='', continuation_token='',
                   start_after='', fetch_owner=False, max_keys=100, ):
        """遍历Bucket里文件的迭代器。
            用法 ::
                >>> for file in self.list_files(prefix='path/'):
                >>>     print(file.key())
                'hello world'

            每次迭代返回的是 :class:`SimplifiedObjectInfo <oss2.models.SimplifiedObjectInfo>` 对象。
            当 `SimplifiedObjectInfo.is_prefix()` 返回True时，表明是公共前缀（目录）。

            :param str match: 正则匹配条件 ; 比如, * 全部匹配， *.jpg只匹配jpg
            :param str prefix: 只罗列文件名为该前缀的文件
            :param str delimiter: 分隔符。可以用来模拟目录
            :param str continuation_token: 分页标志。首次调用传空串，后续使用返回值的next_continuation_token
            :param str start_after: 起始文件名称，OSS会按照文件的字典序排列返回start_after之后的文件。
            :param bool fetch_owner: 是否获取文件的owner信息，默认不返回。
            :param int max_keys: 最多返回文件的个数，文件和目录的和不能超过该值

            :return:
        """
        if prefix.startswith('/'):
            prefix = prefix[1:]

        with tqdm(desc='Get oss files') as pbar:
            for obj in oss2.ObjectIteratorV2(
                    self.bucket, prefix=prefix, delimiter=delimiter, continuation_token=continuation_token,
                    start_after=start_after, fetch_owner=fetch_owner, max_keys=max_keys
            ):
                key = obj.key
                if fnmatch.fnmatch(key, match):
                    pbar.update(1)
                    yield obj

    def download(self, path, *args, **kwargs):
        """下载一个文件。

                用法 ::
                    >>> result = self.download('readme.txt')
                    >>> print(result)
                    'hello world'

                :param path: 文件名
                :return: file-like object
                :raises: 如果文件不存在，则抛出 :class:`NoSuchKey <oss2.exceptions.NoSuchKey>` ；还可能抛出其他异常
        """
        return self.bucket.get_object(key=path, *args, **kwargs).read()

    def upload(self, path, data, *args, **kwargs):
        """上传一个普通文件。

            用法 ::
                >>> self.upload('readme.txt', 'content of readme.txt')
                >>> with open(u'local_file.txt', 'rb') as f:
                >>>     self.upload('remote_file.txt', f)

            :param path: 上传到OSS的文件名
            :param data: 待上传的内容。
            :type data: bytes，str或file-like object

            :return: :class:`PutObjectResult <oss2.models.PutObjectResult>`
        """
        return self.bucket.put_object(key=path, data=data, *args, **kwargs)

    def delete(self, path):
        """删除文件。待删除文件名或文件列表不能为空。

            :param path: str or list of str 文件名 或 文件名列表，不能为空。
            :return:
            :class:`RequestResult <oss2.models.RequestResult>` or
            :class:`BatchDeleteObjectsResult <oss2.models.BatchDeleteObjectsResult>`
        """
        if isinstance(path, list):
            return self.bucket.batch_delete_objects(key_list=path)
        else:
            return self.bucket.delete_object(key=path)
