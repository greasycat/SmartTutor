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
from langchain.prompts import ChatPromptTemplate


class RAG:
    def load_model(self, collection_name: str, model_name=None):
        if model_name is None:
            model_name = "Alibaba-NLP/gte-multilingual-base"

        model_kwargs={"trust_remote_code":True}
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs, )
        self.dimension = len(self.embeddings.embed_query(""))
        print(f"Use collection name: {collection_name}")
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
        return docs
        
    def custom_prompt(self):
        return ChatPromptTemplate.from_template(
            """
            You are a helpful and diligent assistant that can answer questions based on the following context from AI/ML papers:
            {context}


            You are very honest and will say you don't know if you don't know the answer or if the context doesn't contain the answer.
            However, you are very friendly and will try to provide topics that related to the question but not the answer.
            Question: {question}

            """
        )
    
    def search_by_keywords_extraction(self, question:str):
        llm = init_chat_model("gpt-4o-mini", model_provider="openai")
        prompt = ChatPromptTemplate.from_template(
            """
            You are a helpful assistant that can extract or generate keywords from a question.
            Question: {question}

            you will return a list of keywords separated by commas.
            """
        )
        messages = prompt.invoke({"question": question})
        response = llm.invoke(messages)
        retrived_docs = self.store.similarity_search(response.content)
        print(retrived_docs)
        return retrived_docs


    
    def build_rag(self):
        prompt = self.custom_prompt()
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
            docs_content = ""
            for doc in state["context"]:
                docs_content += f"Year: {doc.metadata['year']},\nTitle: {doc.metadata['title']},\nAuthors: {doc.metadata['authors']},\nSummary: {doc.metadata['summary']},\n\n\n"
            messages = prompt.invoke({"question": state["question"], "context": docs_content})
            response = llm.invoke(messages)
            return {"answer": response.content}
        

        graph_builder = StateGraph(State).add_sequence([retrieve, generate])
        graph_builder.add_edge(START, "retrieve")
        graph = graph_builder.compile()

        return graph

    def interactive(self, callback=None):
        # prompt = hub.pull("rlm/rag-prompt")
        print("Welcome to the RAG system!")
        query = ""
        while True:
            query = input("Enter a query (type 'bye' to exit): ")
            if query == "bye":
                print("Exiting RAG system...")
                break
            answer = callback(query)
            print(answer)
            print("-"*100)
    
    def get_rag_callback(self):
        graph = self.build_rag()
        def callback(query):
            state = graph.invoke({"question": query})
            return state["answer"]
        return callback
    
    def get_search_callback(self):
        def callback(query):
            docs = self.similarity_search(query)
            return [doc.metadata for doc in docs]
        return callback
        
        
