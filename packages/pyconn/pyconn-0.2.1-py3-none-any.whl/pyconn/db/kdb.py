import numpy
from qpython import qconnection
from .advancedqreader import AdvancedQReader

from pyconn import logger


class Server:
    def __init__(self, **kwargs):
        self.name = ""
        self.host = ""
        self.port = 0
        self.username = ""
        self.password = ""
        self.timeout = 30.0  # seconds
        self.pandas = False
        self.callback = None
        self.encoding = "utf-8"
        self.__dict__.update(kwargs)

    def to_string(self):
        return self.name


class KDB:
    def __init__(self, server):
        self.server_name = server.name
        self.q = qconnection.QConnection(host=server.host, port=server.port, username=server.username,
                                         password=server.password, encoding=server.encoding,
                                         pandas=server.pandas, reader_class=AdvancedQReader)

    def get_conn(self):
        return self.q

    def close_conn(self):
        self.q.close()

    def query_sync(self, query, *parameters, **options):
        try:
            self.q.open()
            return self.q.sendSync(query, *parameters, **options)
        except ConnectionError as e:
            log_str = "DB[{}] error: {}, query: {}, params: {}, options: {}"
            logger.error(log_str.format(self.server_name, e.args[1], query, parameters, options))
        finally:
            self.close_conn()

    @staticmethod
    def to_sym(s):
        return numpy.string_(s, encoding='utf-8')

    @staticmethod
    def to_sym_list(arr):
        """
        convert numpy.array[object] to numpy.array[numpy.string_ with utf-8]
        :param arr: df['col'].values
        :return: numpy.string_ with utf-8
        """
        if isinstance(arr, list):
            arr = numpy.array(arr)
        return numpy.char.encode(arr.astype(numpy.unicode_), encoding='utf-8')

    @staticmethod
    def to_date(dt):
        return dt.astype('M8[D]')
