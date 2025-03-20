import argparse
import os
from scrape import LoadPapers
from embedding.hf_local import Embedding
import pandas as pd
import ast

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--scrape", action="store_true", default=False, help="Scrape papers")
    parser.add_argument("-g", "--generate_embeddings", action="store_true", default=False, help="Generate embeddings")
    parser.add_argument("-d", "--download_embeddings", action="store_true", default=False, help="Download embeddings")
    parser.add_argument("-i", "--stats", action="store_true", default=False, help="Print stats")
    parser.add_argument("--cache_dir", type=str, default="cache", help="Folder to save the cache")
    parser.add_argument("--data_dir", type=str, default="data", help="Folder to save the data")

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

    if args.generate_embeddings:
        papers = pd.read_csv(os.path.join(data_dir, "papers.csv"))
        embedding = Embedding()
        embedding.load_model()
        embedding.create_embedding_db(papers)
    
    if args.download_embeddings:
        embedding_file = os.path.join(args.cache_dir, "embeddings.tsv")
        meta_file = os.path.join(args.cache_dir, "meta.tsv")

        embedding = Embedding()
        embeddings = embedding.download_embeddings()
        # save to tsv
        # convert the embedding column to a list of floats
        with open(embedding_file, "w") as f:
            for embedding in embeddings["embedding"]:
                embedding = ast.literal_eval(embedding)
                f.write('\t'.join(map(str, embedding)) + '\n')
        
        # save other columns to tsv called meta.tsv
        embeddings[["year", "title", "authors", "summary", "category"]].to_csv(meta_file, sep='\t', index=False)

        print(f"Embeddings saved to {embedding_file}")
        print(f"Meta saved to {meta_file}")

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









if __name__ == "__main__":
    main()