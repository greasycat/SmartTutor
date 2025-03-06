import pandas as pd
import re
import os
import requests
import time
class ArxivScraper:
    def __init__(self, df: pd.DataFrame, cache_dir: str, save_ids: bool = False):
        self.cache_dir = cache_dir

        # create the cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)

        # filter out sites that are not arxiv
        self.df = df[df["sites"] == "arxiv.org"]
        # if ends .pdf or .html, remove it
        self.df["links"] = self.df["links"].str.replace(".pdf", "").str.replace(".html", "")

        # if contains ?, remove it and everything after it
        self.df["links"] = self.df["links"].str.split("?").str[0]

        # if contain %, remove it and everything after it
        self.df["links"] = self.df["links"].str.split("%").str[0]

        # remove duplicates
        self.df = self.df.drop_duplicates(subset=["links"])

        # save only the ids
        self.ids = self.df["links"].str.split("/").str[4]
        # sort by id
        self.ids = sorted(self.ids)

        # remove ids that are not in the format of number.number or number.numbervnumber
        self.ids = [id for id in self.ids if re.match(r"^\d+\.\d+$", id) or re.match(r"^\d+\.\d+v\d+$", id)]

        # save the ids to a file
        if save_ids:
            with open(os.path.join(self.cache_dir, "arxiv_ids.txt"), "w") as f:
                for id in self.ids:
                    f.write(id + "\n")


    def get_ids(self):
        # get the ids from the links
        return self.df["links"].str.split("/").str[4]

    def scrape(self):
        # download the metas
        url = f"https://arxiv.org/api/query?id_list={','.join(self.ids)}&max_results={len(self.ids)}"
        response = requests.get(url)
        # save the response to a file
        with open(os.path.join(self.cache_dir, f"arxiv_metas.xml"), "w") as f:
            f.write(response.text)
        # wait for 4 seconds
        time.sleep(4)
