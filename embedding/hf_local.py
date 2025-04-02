from langchain_huggingface import HuggingFaceEmbeddings
import pandas as pd
from .vector_db import VectorDB
from tqdm import tqdm
class Embedding:
    def __init__(self):
        self.db = VectorDB()
    
    def load_model(self, model_name=None):
        if model_name is None:
            model_name = "Alibaba-NLP/gte-multilingual-base"

        model_kwargs={"trust_remote_code":True}
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs, )

    def _embed_paper(self, papers: pd.DataFrame, table_name: str):
        for _, row in tqdm(papers.iterrows(), total=len(papers)):
            embedding = self.embeddings.embed_query(row["concat"])
            self.db.insert_paper(table_name, row["year"], row["title"], row["authors"], row["summary"], row["category"], embedding)
    
    def create_embedding_db(self, papers: pd.DataFrame, table_name: str):
        self.db.create_table(table_name)
        self._embed_paper(papers, table_name)
    
    def download_embeddings(self, table_name: str):
        return self.db.download_all(table_name)
    