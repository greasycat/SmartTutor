from langchain_huggingface import HuggingFaceEmbeddings
import pandas as pd
from .vector_db import VectorDB
from tqdm import tqdm
class Embedding:
    def __init__(self):
        self.db = VectorDB()
    
    def load_model(self):
        model_kwargs={"trust_remote_code":True}
        model_name = "Alibaba-NLP/gte-multilingual-base"
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs)

    def _embed_paper(self, papers: pd.DataFrame):
        for _, row in tqdm(papers.iterrows(), total=len(papers)):
            embedding = self.embeddings.embed_query(row["concat"])
            self.db.insert_paper(row["year"], row["title"], row["authors"], row["summary"], row["category"], embedding)
    
    def create_embedding_db(self, papers: pd.DataFrame):
        self.db.create_table()
        self._embed_paper(papers)
    
    def download_embeddings(self):
        return self.db.download_all()
    