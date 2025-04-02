import psycopg
import os
import pandas as pd
import pandas.io.sql as sqlio

PASSWORD = os.getenv("VECTOR_DB_PWD")
URL = f"postgresql://postgres:{PASSWORD}@smarttutor.eastus.azurecontainer.io:5432/postgres"


class VectorDB:
    def __init__(self):
        self.conn = psycopg.connect(URL)
        self.cursor = self.conn.cursor()

    def drop_table(self, table_name: str):
        self.cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        self.conn.commit()

    def create_table(self, table_name: str):
        self.drop_table(table_name)
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (
                            id SERIAL PRIMARY KEY, 
                            year INT, 
                            title TEXT, 
                            authors TEXT, 
                            summary TEXT,
                            category TEXT,
                            embedding vector(768) NOT NULL);""")
        self.conn.commit()

    def insert_paper(
        self, table_name: str, year: int, title: str, authors: str, summary: str, category: str, embedding: list[float]
    ):
        self.cursor.execute(
            f"INSERT INTO {table_name} (year, title, authors, summary, category, embedding) VALUES (%s, %s, %s, %s, %s, %s::real[]);",
            (year, title, authors, summary, category, embedding),
        )
        self.conn.commit()
    
    def download_embeddings(self, table_name: str):
        query = f"SELECT embedding FROM {table_name};"
        df = pd.read_sql(query, self.conn)
        return df
    
    def download_all(self, table_name: str):
        query = f"SELECT year, title, authors, summary, category, embedding FROM {table_name};"
        df = sqlio.read_sql_query(query, self.conn)
        return df
