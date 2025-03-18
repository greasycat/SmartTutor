import argparse
from scrape.arxiv_meta_loader import ArxivMetaLoader
from scrape.load_papers import LoadPapers

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scrape", action="store_true")

    args = parser.parse_args()

    if args.scrape:
        load_papers = LoadPapers("data/manually_categorized")
        papers = load_papers.load()
        arxiv_meta_loader = ArxivMetaLoader(papers)
        df = arxiv_meta_loader.loads(["summary"])
        print(df.head())








if __name__ == "__main__":
    main()
