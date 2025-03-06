import argparse
from scrape.readme_scraper import ReadMeScraper
from scrape.arxiv_scraper import ArxivScraper
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scrape", type=str, default="readme")

    args = parser.parse_args()

    if args.scrape == "readme":
        readme_scraper = ReadMeScraper("readme_collections.txt", "cache/readme/links.csv")
        df = readme_scraper.scrape()
        arxiv_scraper = ArxivScraper(df, "cache/arxiv", save_ids=True)
        arxiv_scraper.scrape()






if __name__ == "__main__":
    main()
