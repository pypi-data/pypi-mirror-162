import cx_Oracle as odb
import pandas


class OracleServerInfo:
    def __init__(self):
        self.name = ""
        self.sid = ""
        self.username = ""
        self.password = ""
        self.pandas = False

    def to_string(self):
        return self.name


class ORACLE:
    def __init__(self, server):
        self.conn_str = server.username + "/" + server.password + "@" + server.sid
        self.conn = None
        self.name = server.name

    def get_conn(self):
        self.conn = odb.connect(self.conn_str)
        return self.conn

    def close_conn(self):
        self.conn.close()

    def query_pandas(self, query, parameters={}):
        self.get_conn()
        try:
            return pandas.read_sql(query, self.conn, params=parameters)
        except Exception as e:
            print("ORACLE[%s] error code: %s, msg: %s", self.name, str(e.args[0]), str(e.args[1]))
            print("query: %s", query)
            print("parameters: %s", parameters)
        finally:
            self.close_conn()

    def query(self, query, parameters={}):
        self.get_conn()
        cur = self.conn.cursor()
        try:
            return cur.execute(query, parameters)
        except Exception as e:
            print("ORACLE[%s] error code: %s, msg: %s", self.name, str(e.args[0]), str(e.args[1]))
            print("query: %s", query)
            print("parameters: %s", parameters)
        finally:
            self.conn.commit()
            cur.close()
            self.close_conn()
