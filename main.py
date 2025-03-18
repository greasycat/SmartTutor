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
        papers = load_papers.load()

        arxiv_meta_loader = ArxivMetaLoader(papers, cache_dir)
        arxiv_df = arxiv_meta_loader.loads()

        meta_scrape_loader = MetaScrapeLoader(papers, cache_dir)
        nature_df = meta_scrape_loader.load_nature()
        ieee_df = meta_scrape_loader.load_ieee()
        jmlr_df = meta_scrape_loader.load_jmlr()
        nips_df = meta_scrape_loader.load_neurips()
        springer_df = meta_scrape_loader.load_springer()
        acm_df = meta_scrape_loader.load_acm()
        sciencedirect_df = meta_scrape_loader.load_sciencedirect()
        manual_df = meta_scrape_loader.load_manual()
        print(manual_df.head())

        concat_df = pd.concat([nature_df, ieee_df, jmlr_df, nips_df, springer_df, acm_df, sciencedirect_df, arxiv_df, manual_df])

        try:
            concat_df["len(summary)"] = concat_df["summary"].apply(len)
        except TypeError:
            warnings.warn("Warning: Some summaries are not strings, which means either the summary is not available or the script failed to parse it")




if __name__ == "__main__":
    main()
