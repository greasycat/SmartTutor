import argparse
import os
from scrape import LoadPapers
from embedding.hf_local import Embedding
from embedding.vector_db import VectorDB
import pandas as pd
import ast

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scrape", action="store_true", default=False)
    parser.add_argument("--cache_dir", type=str, default="cache")
    parser.add_argument("--data_dir", type=str, default="data")
    parser.add_argument("--generate_embeddings", action="store_true", default=False)
    parser.add_argument("--download_embeddings", action="store_true", default=False)

    args = parser.parse_args()
    paper_cache_dir = os.path.join(args.cache_dir, "papers")
    os.makedirs(paper_cache_dir, exist_ok=True)

    papers_dir = os.path.join(args.data_dir, "manually_categorized")

    if args.scrape:
        load_papers = LoadPapers(papers_dir)
        papers = load_papers.load(paper_cache_dir)
        # check max dim
        print("Max dimension:", papers["dim"].max())

        # print the number of papers in each category
        print(papers["year"].value_counts())

        # save the papers to a csv file
        papers.to_csv(os.path.join(papers_dir, "papers.csv"), index=False)

    if args.generate_embeddings:
        papers = pd.read_csv(os.path.join(papers_dir, "papers.csv"))
        embedding = Embedding()
        embedding.create_embedding_db(papers)
    
    if args.download_embeddings:
        vector_db = VectorDB()
        embeddings = vector_db.download_embeddings()
        # save to tsv
        # convert the embedding column to a list of floats
        with open(os.path.join(args.cache_dir, "embeddings.tsv"), "w") as f:
            for embedding in embeddings["embedding"]:
                embedding = ast.literal_eval(embedding)
                f.write('\t'.join(map(str, embedding)) + '\n')






if __name__ == "__main__":
    main()