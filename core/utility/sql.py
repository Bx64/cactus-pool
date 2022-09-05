import sqlite3
from datetime import datetime
from pathlib import Path

class Sql:
    def __init__(self):
        self.home = str(Path.home())
        self.data_path = self.home+'/.local/share/solar-core/testnet/tbw/tbw.db'

        
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
