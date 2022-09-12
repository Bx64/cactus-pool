import sqlite3
from config.pool_config import PoolConfig
from pathlib import Path


# get configuration
poolconfig = PoolConfig()
if (poolconfig.error):
    print("FATAL: pool_config.ini not found! Terminating POOL.", file=sys.stderr)
    sys.exit(1)

class Sql:
    def __init__(self):
        self.home = str(Path.home())
        self.data_path = self.home+'/.local/share/solar-core/{}/tbw/tbw.db'.format(poolconfig.network)

    def open_connection(self):
        self.connection = sqlite3.connect(self.data_path)
        self.cursor = self.connection.cursor()

    def close_connection(self):
        self.cursor.close()
        self.connection.close()

    def fetchall(self):
        return self.cursor.fetchall()

    def history(self):
        return self.cursor.execute("SELECT * FROM history ORDER BY timestamp DESC LIMIT 1000")
