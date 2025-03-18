import argparse
import os
from scrape import ArxivMetaLoader, MetaScrapeLoader, LoadPapers
import pandas as pd
import warnings

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scrape", action="store_true")
    parser.add_argument("--cache_dir", type=str, default="cache/papers")

    args = parser.parse_args()
    cache_dir = args.cache_dir
    os.makedirs(cache_dir, exist_ok=True)

    if args.scrape:
        load_papers = LoadPapers("data/manually_categorized")
        papers = load_papers.load(cache_dir)
        papers.to_csv("data/papers.csv", index=False)





if __name__ == "__main__":
    main()
