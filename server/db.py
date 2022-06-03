import psycopg2 as pg2

class DB():
    
    def __init__(self):
        self.psql_hostname = 'localhost'
        self.psql_dbname = 'krx'
        self.psql_user = 'postgres'
        self.psql_password = 'SECRET'
        self.psql_port = 5432
        self.conn = None
    
    def connect(self):
        self.conn = pg2.connect(
            database=self.psql_dbname,
            user=self.psql_user,
            password=self.psql_password,
            host=self.psql_hostname,
            port= self.psql_port
        )
        # set read only
        self.conn.set_session(readonly = True)
        
    def disconnect(self):
        self.conn.close()
        
    def query(self, query_str:str):
        cur = self.conn.cursor()
        try:
            cur.execute(query_str)
            result = cur.fetchall()
        except Exception as e:
            self.conn.rollback()
            raise Exception("db error!")
        return result
