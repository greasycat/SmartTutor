import os
import pandas as pd
import xml.etree.ElementTree as ET

class LoadPapers:
    def __init__(self, folder: str):
        self.folder = folder

    def load(self):
        # get all the files in the folder and create a list of categories based on the filename
        categories = []
        for file in os.listdir(self.folder):
            categories.append(file.split(".")[0])
        categories = list(set(categories))

        # load the papers
        columns = ["Year", "Paper", "Authors", "Link", "Category"]
        papers = pd.DataFrame(columns=columns)

        for category in categories:
            df = pd.read_csv(os.path.join(self.folder, f"{category}.csv"), index_col=False)
            df["Category"] = category
            df = df.fillna("na")
            papers = pd.concat([papers, df])

        # reset the index
        papers = papers.reset_index(drop=True)
        # set all NA values to None
        return papers



if __name__ == "__main__":
    load_papers = LoadPapers("data/manually_categorized")
    papers = load_papers.load()
    print(papers.head())
    # save the papers to a csv file
    # set all NA values to None
    papers = papers.fillna("na")
    papers.to_csv("data/papers.csv", index=False)
