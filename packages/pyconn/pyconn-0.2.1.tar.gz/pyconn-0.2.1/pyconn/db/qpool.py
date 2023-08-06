import time
import threading
import os

import numpy
from qpython.qconnection import QConnection

from pyconn import logger
from pyconn.db.advancedqreader import AdvancedQReader


class Server:
    def __init__(self, **kwargs):
        self.name = ''
        self.host = ''
        self.port = 0
        self.username = ''
        self.password = ''
        self.timeout = 15.0  # seconds
        self.pandas = False
        self.callback = None
        self.encoding = 'utf-8'
        self.__dict__.update(kwargs)


class MonitorThread(threading.Thread):
    def __init__(self):
        super(MonitorThread, self).__init__()
        self.pool = ConnectionPool()

    def run(self):
        while True:
            if self.pool is not None:
                for server_name, handle in self.pool.handle_dict.items():
                    if handle.is_connected:
                        try:
                            with handle.lock:
                                handle.sendSync('til 1')
                                logger.debug(f'{server_name} heartbeat success')
                        except Exception as e:
                            logger.info(f'{server_name} heartbeat failed')
                            handle.is_connected = False
                    else:
                        handle = self.pool.create_connection(handle.server)
                        if handle is not None and handle.is_connected:
                            logger.info(f'Reconnected to {handle.server.name}')
                            callback = handle.server.callback
                            if callable(callback):
                                callback()
                time.sleep(self.pool.heartbeat)


class QHandle(QConnection):
    def __init__(self, server):
        super(QHandle, self).__init__(host=server.host, port=server.port, username=server.username,
                                      encoding=server.encoding, timeout=server.timeout, password=server.password,
                                      pandas=server.pandas, reader_class=AdvancedQReader)
        self.is_connected = False
        self.server = server
        self.lock = threading.Lock()


class ConnectionPool:
    _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls, server_list=None, heartbeat=15.0):
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super(ConnectionPool, cls).__new__(cls)
                    cls._instance.heartbeat = heartbeat
                    cls._instance.handle_dict = {}
                    cls._instance.thread = MonitorThread()
                    if not cls._instance.thread.is_alive():
                        cls._instance.start_monitor_thread()
        return cls._instance

    def __init__(self, server_list=None, heartbeat=15.0):
        if server_list is None:
            return
        if isinstance(server_list, Server):
            server_list = [server_list]
        self.heartbeat = heartbeat
        for server in server_list:
            if server.name not in self.handle_dict.keys():
                self.create_connection(server)

    def __del__(self):
        for name, conn in self.handle_dict.items():
            conn.close()
            logger.info(f'DB[{name}] connection closed')

    def start_monitor_thread(self):
        logger.info(f'Process[{os.getpid()}], Thread[{threading.get_ident()}], starting connection monitoring thread')
        self.thread.start()

    def create_connection(self, server):
        with self._instance_lock:
            conn = QHandle(server)
            self.handle_dict[server.name] = conn
            try:
                logger.info(f'Process[{os.getpid()}], Thread[{threading.get_ident()}], try connect to {server.name}')
                with conn.lock:
                    conn.open()
            except Exception as e:
                logger.info(f'Connect to {server.name} failed: {e.args}')
                conn.is_connected = False
            else:
                logger.info(f'Process[{os.getpid()}], Thread[{threading.get_ident()}], DB[{server.name}] connected')
                conn.is_connected = True
            return conn

    def get_connection(self, server):
        with self._instance_lock:
            return self.handle_dict.get(server.name)


class Query:

    def __init__(self, server):
        self.server = server
        self.pool = ConnectionPool(self.server)
        self.conn = self.pool.get_connection(self.server)

    def query_sync(self, query, *parameters, **options):
        result = None
        self.conn = self.pool.get_connection(self.server)
        if self.conn is not None and self.conn.is_connected:
            try:
                with self.conn.lock:
                    result = self.conn.sendSync(query, *parameters, **options)
            except Exception as e:
                log_str = f'DB[{self.server.name}] error: {e.args}, query: {query}, params: {parameters}, options: {options}'
                logger.error(log_str)
        else:
            log_str = f'Process[{os.getpid()}], Thread[{threading.get_ident()}], DB[{self.server.name}] error: Invalid handle, query: {query}, params: {parameters}, options: {options}'
            logger.error(log_str)
        return result

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
