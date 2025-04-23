import argparse
import os
import uvicorn
from scrape import LoadPapers
import pandas as pd
import ast
import re
from embedding.rag import RAG
from embedding.vector_db import VectorDB

def check_table_name_valid(table_name: str):
    # check if the table name is with regex 
    # name must start with a letter and contain only letters, numbers, and underscores
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', table_name):
        raise ValueError("Table name must start with a letter and contain only letters, numbers, and underscores")

def main():
    parser = argparse.ArgumentParser()
    
    # exclude -g and -d
    parser.add_argument("-s", "--scrape", action="store_true", default=False, help="Scrape papers")

    parser.add_argument("-g", "--generate_embeddings", type=str, default="", help="Generate embeddings and save to a table")

    # make download_embeddings accept a table name
    parser.add_argument("-d", "--download_embeddings", type=str, default="", help="Download embeddings from a table")

    parser.add_argument("-i", "--stats", action="store_true", default=False, help="Print stats")
    parser.add_argument("--cache_dir", type=str, default="cache", help="Folder to save the cache")
    parser.add_argument("--data_dir", type=str, default="data", help="Folder to save the data")
    parser.add_argument("--model", type=str, default="Alibaba-NLP/gte-multilingual-base", help="Model name")
    parser.add_argument("--rag", type=str, default="", help="Run RAG with a collection name")
    parser.add_argument("--search", type=str, default="", help="Search for relevant papers with a collection name")
    parser.add_argument("--api", type=str, default="", help="Run API with a collection name")
    parser.add_argument("--api_port", type=int, default=8000, help="API port")
    parser.add_argument("--api_host", type=str, default="0.0.0.0", help="API host")

    args = parser.parse_args()
    paper_cache_dir = os.path.join(args.cache_dir, "papers")
    os.makedirs(paper_cache_dir, exist_ok=True)

    papers_dir = os.path.join(args.data_dir, "manually_categorized")
    data_dir = args.data_dir

    if args.scrape:
        load_papers = LoadPapers(papers_dir)
        papers = load_papers.load(paper_cache_dir)
        # check max dim
        print("Max dimension:", papers["dim"].max())

        # print the number of papers in each category
        print(papers["year"].value_counts())

        # save the papers to a csv file
        papers.to_csv(os.path.join(data_dir, "papers.csv"), index=False)

    if args.generate_embeddings != "":
        check_table_name_valid(args.generate_embeddings)
        papers = pd.read_csv(os.path.join(data_dir, "papers.csv"))
        embedding = RAG()
        embedding.load_model(args.generate_embeddings, args.model)
        embedding.embed_papers(papers)
        print(f"Embeddings generated for {args.generate_embeddings}")
    
    if args.download_embeddings != "":
        check_table_name_valid(args.download_embeddings)
        embedding_file = os.path.join(args.cache_dir, f"{args.download_embeddings}_embeddings.tsv")
        meta_file = os.path.join(args.cache_dir, f"{args.download_embeddings}_meta.tsv")
        vector_db = VectorDB()
        table_name = f"collection_{args.download_embeddings}"

        meta = vector_db.download_meta(table_name)
        meta = [x[0] for x in meta]
        df = pd.DataFrame(meta)
        df.to_csv(meta_file, sep='\t', index=False)

        # save to tsv
        embeddings = vector_db.download_embeddings(table_name)
        with open(embedding_file, "w") as f:
            for embedding in embeddings:
                embedding = ast.literal_eval(embedding[0])
                f.write('\t'.join(map(str, embedding)) + '\n')
        
        print(f"Embeddings saved to {embedding_file}")
        print(f"Meta saved to {meta_file}")
    
    if args.rag != "":
        rag = RAG()
        rag.load_model(args.rag, args.model)
        rag.interactive(callback=rag.get_rag_callback())
    
    if args.search != "":
        rag = RAG()
        rag.load_model(args.search, args.model)
        rag.interactive(callback=rag.get_search_callback())

    if args.stats:
        description_dict = {
            "audio": "Audio",
            "cv_generative": "Computer Vision Generative Models",
            "cv_pattern": "Computer Vision Pattern Recognition",
            "dl_nlp": "Deep Learning for NLP",
            "dl_rl": "Deep Learning for Reinforcement Learning",
            "dl_rnn": "Deep Learning with RNNs",
            "ml_general": "General Machine Learning",
        }
        papers = pd.read_csv(os.path.join(data_dir, "papers.csv"))
        # count the number of papers in each category and convert to a df
        category_counts = papers["category"].value_counts().reset_index()
        # add the description to the df
        category_counts["description"] = category_counts["category"].map(description_dict)
        # print the df in markdown format
        print(category_counts.to_markdown())

    if args.api != "":
        from api import create_app
        app = create_app(args.api)
        uvicorn.run(app, host=args.api_host, port=args.api_port)









if __name__ == "__main__":
    main()