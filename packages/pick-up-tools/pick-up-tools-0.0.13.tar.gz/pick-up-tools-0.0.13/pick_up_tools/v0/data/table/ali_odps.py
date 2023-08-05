"""
Aliyun ODPS

"""
import platform
import multiprocessing
from pandas import DataFrame
from odps import ODPS as ALiODPS


class ODPSTable(object):
    def __init__(self, odps: ALiODPS, table_name, project=None):
        self._odps = odps
        self.table = self._odps.get_table(name=table_name, project=project)
        self._n_process = 1 if platform.system() == 'Windows' else multiprocessing.cpu_count()

    def insert(self, records: list, partition=None, create_partition=False):
        """
        :param records: list of list or list of dict
        :param partition: partition expression, example: 'pt=20220630'
        :return: None
        """
        tb = self.table
        columns = tb.schema.names
        if isinstance(records[0], dict):
            _records = []
            for i in records:
                _records.append([i.get(ii) for ii in columns])
            records = _records
        with tb.open_writer(partition=partition, create_partition=create_partition) as writer:
            writer.write(records)

    def read(self, partition=None) -> DataFrame:
        tb = self.table
        with tb.open_reader(partition=partition) as reader:
            df = reader.to_pandas(self._n_process)
        return df


class ODPS(object):
    """
    Main entrance to ODPS.

    Convenient operations on ODPS objects are provided.
    Please refer to `ODPS docs <https://docs.aliyun.com/#/pub/odps/basic/definition&project>`_
    to see the details.

    Generally, basic operations such as ``list``, ``get``, ``exist``, ``create``, ``delete``
    are provided for each ODPS object.
    Take the ``Table`` as an example.

    To create an ODPS instance, access_id and access_key is required, and should ensure correctness,
    or ``SignatureNotMatch`` error will throw. If `tunnel_endpoint` is not set, the tunnel API will
    route service URL automatically.

    :param access_id: Aliyun Access ID
    :param access_secret: Aliyun Access Key
    :param project: default project name
    :param endpoint: Rest service URL

    :Example:

    >>> odps = ODPS('default_project', '**your access id**', '**your access key**')
    >>>
    >>> for table in odps.list_tables():
    >>>    # handle each table
    >>>
    >>> table = odps.table('dual')
    >>>
    >>> odps.exist_table('dual') is True
    >>>
    >>> table.create('test_table', schema)
    >>>
    >>> odps.odps.delete('test_table')
    """

    def __init__(self, project, access_id, access_secret,
                 endpoint='https://oss-cn-hangzhou.aliyuncs.com',
                 *args, **kwargs):
        self.odps = ALiODPS(project=project, access_id=access_id, secret_access_key=access_secret,
                            endpoint=endpoint, *args, **kwargs)

    def list_tables(self, project=None, prefix=None, owner=None):
        """
        List all tables of a project.
        If prefix is provided, the listed tables will all start with this prefix.
        If owner is provided, the listed tables will be belong to such owner.

        :param project: 项目空间名
        :param prefix: 限定搜索前缀
        :param owner: 限定所有者
        :return: tables in this project, filtered by the optional prefix and owner.
        :rtype: generator
        """
        return self.odps.list_tables(project=project, prefix=prefix, owner=owner)

    def exist_table(self, table_name):
        return self.odps.exist_table(table_name)

    def create_table(self, table_name, schema, if_not_exists=True, lifecycle=None, **kwargs):
        return self.odps.create_table(
            table_name, schema, if_not_exists=if_not_exists, lifecycle=lifecycle, **kwargs)

    def table(self, table_name, project=None) -> ODPSTable:
        return ODPSTable(odps=self.odps, table_name=table_name, project=project)
