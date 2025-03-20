import os
import pandas as pd
from .arxiv_meta_loader import ArxivMetaLoader
from .meta_scrape_loader import MetaScrapeLoader
from .utils import clean_text_for_embedding

class LoadPapers:
    def __init__(self, folder: str):
        self.folder = folder

    def _load_raw(self):
        # get all the files in the folder and create a list of categories based on the filename
        categories = []
        for file in os.listdir(self.folder):
            categories.append(file.split(".")[0])
        categories = list(set(categories))

        # load the papers
        columns = ["year", "title", "authors", "link", "category"]
        papers = pd.DataFrame(columns=columns)

        for category in categories:
            df = pd.read_csv(os.path.join(self.folder, f"{category}.csv"), index_col=False)
            df["category"] = category
            df = df.fillna("na")
            papers = pd.concat([papers, df])

        # reset the index
        papers = papers.reset_index(drop=True)
        lower_column = [col.lower() for col in papers.columns]
        papers.columns = lower_column

        # set all NA values to None
        return papers
    
    def load(self, cache_dir: str):
        papers = self._load_raw()
        # check NA values
        print(papers.isna().sum())
        # print NA rows
        print(papers[papers["link"].isna()])

        # abort if there are any NA values
        if papers["link"].isna().any():
            raise ValueError("There are NA values in the link column")

        print("loading arxiv metas")
        arxiv_meta_loader = ArxivMetaLoader(papers, cache_dir)
        arxiv_df = arxiv_meta_loader.loads()

        print("loading meta scrape")
        meta_scrape_loader = MetaScrapeLoader(papers, cache_dir)
        nature_df = meta_scrape_loader.load_nature()
        ieee_df = meta_scrape_loader.load_ieee()
        jmlr_df = meta_scrape_loader.load_jmlr()
        nips_df = meta_scrape_loader.load_neurips()
        springer_df = meta_scrape_loader.load_springer()
        acm_df = meta_scrape_loader.load_acm()
        sciencedirect_df = meta_scrape_loader.load_sciencedirect()
        manual_df = meta_scrape_loader.load_manual()

        # print all the columns of all the dataframes
        concat_df = pd.concat([nature_df, ieee_df, jmlr_df, nips_df, springer_df, acm_df, sciencedirect_df, arxiv_df, manual_df])

        return self.clean(concat_df)
    
    def clean(self, df: pd.DataFrame):
        # sort by summary length
        print(df.head(10))
        df["summary"] = df["summary"].apply(clean_text_for_embedding)
        df["title"] = df["title"].apply(clean_text_for_embedding)
        df["authors"] = df["authors"].apply(clean_text_for_embedding)
        df["concat"] = df["title"] + " " + df["authors"] + " " + df["summary"]
        df["dim"] = df["concat"].apply(lambda x: len(x.split(" ")))

        return df


