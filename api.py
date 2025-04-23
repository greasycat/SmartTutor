from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from embedding.rag import RAG

def create_app(model_name):
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )
    
    # Initialize RAG with specified model
    rag = RAG()
    rag.load_model(model_name)
    rag_callback = rag.get_rag_callback()
    search_callback = rag.get_search_callback()
    
    @app.get("/rag/")
    def rag_endpoint(question: str):
        try:
            answer = rag_callback(question)
            return {"answer": answer}
        except Exception as e:
            return {"error": str(e)}
    
    @app.get("/search/")
    def search_endpoint(query: str):
        try:
            answer = search_callback(query)
            return {"results": answer}
        except Exception as e:
            return {"error": str(e)}
    
    @app.get("/")
    def read_root():
        return {"message": f"RAG API running with model: {model_name}"}
    
    return app