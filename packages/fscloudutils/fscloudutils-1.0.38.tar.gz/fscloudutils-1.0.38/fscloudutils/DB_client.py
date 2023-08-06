
import mysql.connector
from mysql.connector.errors import Error as MySQLError
import pandas as pd
from pandas import DataFrame

# dir_path = os.path.dirname(sys.argv[0])
# os.chdir(dir_path)
'''tables = ['fruit_variety', 'project', 'project_plot', 'plot', 'customer','caliber']'''


class DBClient:
    def __init__(self, db_server: str, db_user: str, db_password: str, db_name: str):
        self._connector = None
        self._cursor = None
        self.db_server = db_server
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name

    def connect(self):
        self._connector = mysql.connector.connect(
            host=self.db_server,
            user=self.db_user,
            password=self.db_password,
            database=self.db_name)
        self._cursor = self._connector.cursor()

    def execute(self, SQL_command: str, params=()) -> None:
        try:
            self.connect()
            self._cursor.execute(SQL_command, params=params)
            self._connector.commit()
        except MySQLError:
            pass
        finally:
            self.close_connection()

    def select(self, SQL_command: str, params=()) -> pd.DataFrame:
        try:
            self.connect()
            self._cursor.execute(SQL_command, params=params)
            df = DataFrame(self._cursor.fetchall(), columns=[i[0] for i in self._cursor.description])
            return df
        except MySQLError:
            pass
        finally:
            self.close_connection()

    def close_connection(self):
        try:
            self._cursor.close()
        except MySQLError:
            pass
        try:
            self._connector.close()
        except MySQLError:
            pass
