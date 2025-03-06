from .downloader import Downloader
import re
import pandas as pd

# This class is used to scrape all the links
class ReadMeScraper:
    def __init__(self, collection_file: str, output_file: str):
        self.output_file = output_file
        self.collection_file = collection_file
        self.folders = []
        with open(self.collection_file, "r") as f:
            for line in f:
                if line.strip():
                    self.folders.append(line.strip())

        self.downloaders = []
        for folder in self.folders:
            self.downloaders.append(Downloader(folder, "cache/readme"))

    def scrape(self):
        self.links = []
        for downloader in self.downloaders:
            content = downloader.get()
            # find all the links in the content with regex
            url_pattern = re.compile(r'https?://[^\s<>"\(\)]+|www\.[^\s<>"\(\)]+')
            urls = url_pattern.findall(content)
            self.links.extend(urls)

        # replace all http with https
        tuples = []

        for i, link in enumerate(self.links):
            self.links[i] = link.replace("http", "https")

            # get the site name
            site = link.split("/")[2]

            # check if the url is a pdf
            if link.endswith(".pdf"):
                type = "pdf"
            else:
                type = "html"

            tuples.append((link, site, type))

        # remove duplicates
        tuples = list(set(tuples))
        # save the links to a csv file
        self.df = pd.DataFrame(tuples, columns=["links", "sites", "types"])
        self.df.to_csv(self.output_file, index=False)
        return self.df
    
    def summary(self):
        # get the number of links for each site
        print(self.df["sites"].value_counts())
        # get the number of links for each type
        print(self.df["types"].value_counts())


        