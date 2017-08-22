import pymysql

class MySQL():

    def __init__(self, host, user, password, port):
        self._host = host
        self._user = user
        self._password = password
        self._conn = pymysql.connect(host=host, port=port,
                       user=user, passwd=password)
        self._cursor = self._conn.cursor()

    def execute(self, query):
        try:
            self._cursor.execute(query=query)
        except (AttributeError, pymysql.OperationalError):
            self.__reconnect__()
            self._cursor.execute(query=query)

    def fetchone(self):
        return self._cursor.fetchone()

    def commit(self):
        return self._conn.commit()

    def __reconnect__(self):
        self._conn = pymysql.connect(host=self._host, port=self._port, user=self._user, passwd=self._password)
        self._cursor = self._conn.cursor()
