import argparse
from scrape.link_scraper import LinkScraper
from scrape.arxiv_scraper import ArxivScraper
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scrape", action="store_true")

    args = parser.parse_args()

    if args.scrape:
        link_scraper = LinkScraper("data/collections.txt", "cache/plaintext/links.csv")
        df = link_scraper.scrape()
        arxiv_scraper = ArxivScraper(df, "data/", "cache/arxiv", save_ids=True)
        arxiv_scraper.scrape()






if __name__ == "__main__":
    main()
