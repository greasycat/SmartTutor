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

    # def create_table(self, table_name: str):
    #     self.drop_table(table_name)
    #     self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (
    #                         id SERIAL PRIMARY KEY, 
    #                         year INT, 
    #                         title TEXT, 
    #                         authors TEXT, 
    #                         summary TEXT,
    #                         category TEXT,
    #                         embedding vector(768) NOT NULL);""")
    #     self.conn.commit()

    # def insert_paper(
    #     self, table_name: str, year: int, title: str, authors: str, summary: str, category: str, embedding: list[float]
    # ):
    #     self.cursor.execute(
    #         f"INSERT INTO {table_name} (year, title, authors, summary, category, embedding) VALUES (%s, %s, %s, %s, %s, %s::real[]);",
    #         (year, title, authors, summary, category, embedding),
    #     )
    #     self.conn.commit()
    
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
