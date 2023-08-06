'''
Driver wrapper for sqlite3
'''
import sqlite3

class DriverSQLite():
    '''
    Driver wrapper for sqlite3
    Provides a uniform interface to SQL user code
    '''
    TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

    def __init__(self, connectionInfo):
        '''
        Constructor
        :param connectionInfo: dictionary having the items needed to connect to SQLite server
                { 'LocalDatabaseFile' : <path str> }
        '''
        self.localDatabaseFile = connectionInfo['localDatabaseFile']
        self.connect()
        
    def connect(self):
        '''
        Connect to the database.
        :return True/False
        '''
        self.connection = None
        try:
            self.connection = sqlite3.connect(self.localDatabaseFile)
            cursor = self.connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            return True
        except Exception as e:
            print(f"SQLite error: {e}")
            return False

    def disconnect(self):
        '''
        Disconnect from the database.
        :return True/False
        '''
        try:
            self.connection.close()
            self.connection = None
            self.cursor = None
            return True
        except Exception as e:
            print(f"SQLite error: {e}")
            return False
        
    def execute(self, query, params = None, commit = False):
        '''
        Execute an SQL query.
        :param query: str
        :param params: tuple or dictionary params are bound to the variables in the operation. 
                       Specify variables using %s or %(name)s parameter style (that is, using format or pyformat style).
        :param commit: If True, commit INSERT/UPDATE/DELETE queries immediately.
        :return True/False
        '''
        self.cursor = self.connection.cursor()
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            if commit:
                self.connection.commit()
            return True
        except Exception as e:
            print(f"SQLite error: {e}")
            return False
    
    def executemany(self, query, params, commit = False):
        '''
        Executes a parameterized SQL command against all params.  For bulk insert.
        :param params: tuple or dictionary params are bound to the variables in the operation. 
                       Specify variables using %s or %(name)s parameter style (that is, using format or pyformat style).
        :param commit: If True, commit INSERT/UPDATE/DELETE queries immediately.
        :return True/False
        '''
        self.cursor = self.connection.cursor()
        try:
            self.cursor.executemany(query, params)
            if commit:
                self.connection.commit()
            return True
        except Exception as e:
            print(f"SQLite error: {e}")
            return False
        
    def commit(self):
        '''
        Commit any previously executed but not yet committed INSERT/UPDATE/DELETE queries.
        :return True/False
        '''
        try:
            self.connection.commit()
            return True
        except Exception as e:
            print(f"SQLite error: {e}")
            return False
        
    def rollback(self):
        '''
        Rollback any previously executed but not yet committed INSERT/UPDATE/DELETE queries.
        :return True/False
        '''
        try:
            self.connection.rollback()
            return True
        except Exception as e:
            print(f"SQLite error: {e}")
            return False

    def fetchone(self):
        '''
        Fetch one row from the last SELECT query.
        :return tuple or False
        '''
        try:
            row = self.cursor.fetchone()
            return row
        except Exception as e:
            print(f"SQLite error: {e}")
            return False

    def fetchmany(self, chunkSize):
        '''
        Fetch multiple rows from the last SELECT query.
        :param chunkSize: max number of rows to fetch
        :return list of tuple or False
        '''
        try:
            result = self.cursor.fetchmany(chunkSize)
            return result
        except Exception as e:
            print(f"SQLite error: {e}")
            return False

    def fetchall(self):
        '''
        Fetch all rows from the last SELECT query.
        :return list of tuple or False
        '''
        try:
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(f"SQLite error: {e}")
            return False
