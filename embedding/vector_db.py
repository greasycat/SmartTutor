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

    def drop_table(self):
        self.cursor.execute("DROP TABLE IF EXISTS resources;")
        self.conn.commit()

    def create_table(self):
        self.drop_table()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS resources (
                            id SERIAL PRIMARY KEY, 
                            year INT, 
                            title TEXT, 
                            authors TEXT, 
                            summary TEXT,
                            category TEXT,
                            embedding vector(768) NOT NULL);""")

    def insert_paper(
        self, year: int, title: str, authors: str, summary: str, category: str, embedding: list[float]
    ):
        self.cursor.execute(
            "INSERT INTO resources (year, title, authors, summary, category, embedding) VALUES (%s, %s, %s, %s, %s, %s::real[]);",
            (year, title, authors, summary, category, embedding),
        )
        self.conn.commit()
    
    def download_embeddings(self):
        query = "SELECT embedding FROM resources;"
        df = pd.read_sql(query, self.conn)
        return df
    
    def download_all(self):
        query = "SELECT year, title, authors, summary, category, embedding FROM resources;"
        df = sqlio.read_sql_query(query, self.conn)
        return df
