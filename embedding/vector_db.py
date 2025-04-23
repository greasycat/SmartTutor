import psycopg
import pandas as pd
from .env import URL


class VectorDB:
    def __init__(self):
        self.conn = psycopg.connect(URL())
        self.cursor = self.conn.cursor()

    def drop_table(self, table_name: str):
        self.cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        self.conn.commit()

    def download_embeddings(self, table_name: str):
        query = f"SELECT embedding FROM \"{table_name}\";"
        self.cursor.execute(query)
        embeddings = self.cursor.fetchall()
        return embeddings
    
    def download_meta(self, table_name: str):
        query = f"SELECT meta FROM \"{table_name}\";"
        self.cursor.execute(query)
        meta = self.cursor.fetchall()
        return meta
