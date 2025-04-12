from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores.pgvecto_rs import PGVecto_rs
from langchain_core.documents import Document
import pandas as pd
from tqdm import tqdm
from .env import URL, OPENAI_API_KEY

from langchain.chat_models import init_chat_model

from langchain import hub
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict


class RAG:
    def load_model(self, collection_name: str, model_name=None):
        if model_name is None:
            model_name = "Alibaba-NLP/gte-multilingual-base"

        model_kwargs={"trust_remote_code":True}
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs, )
        self.dimension = len(self.embeddings.embed_query(""))
        self.store = PGVecto_rs(
            collection_name=collection_name,
            db_url=URL(),
            embedding=self.embeddings,
            dimension=self.dimension
        )
    
    def _embed_paper(self, papers: pd.DataFrame):
        for _, row in tqdm(papers.iterrows(), total=len(papers)):
            document = Document(page_content=row["concat"],
                                metadata={
                                    "year": row["year"],
                                    "title": row["title"],
                                    "authors": row["authors"],
                                    "summary": row["summary"],
                                    "category": row["category"]
                                })
            self.store.add_documents([document])
    
    def embed_papers(self, papers: pd.DataFrame):
        self._embed_paper(papers)
    
    def similarity_search(self, query:str, k:int=10):
        docs = self.store.similarity_search(query, k=k)
        for doc in docs:
            print(doc.page_content)
            print(doc.metadata)
            print("-"*100)
    
    def build_and_run(self):
        prompt = hub.pull("rlm/rag-prompt")
        OPENAI_API_KEY()
        llm = init_chat_model("gpt-4o-mini", model_provider="openai")

        class State(TypedDict):
            question: str
            context: List[Document]
            answer: str


        # Define application steps
        def retrieve(state: State):
            retrieved_docs = self.store.similarity_search(state["question"])
            return {"context": retrieved_docs}


        def generate(state: State):
            docs_content = "\n\n".join(doc.page_content for doc in state["context"])
            messages = prompt.invoke({"question": state["question"], "context": docs_content})
            response = llm.invoke(messages)
            return {"answer": response.content}

        graph_builder = StateGraph(State).add_sequence([retrieve, generate])
        graph_builder.add_edge(START, "retrieve")
        graph = graph_builder.compile()

        print("Welcome to the RAG system!")
        query = ""
        while True:
            query = input("Enter a query (type 'bye' to exit): ")
            if query == "bye":
                print("Exiting RAG system...")
                break
            state = graph.invoke({"question": query})
            print(state["answer"])
            print("-"*100)
        
        
