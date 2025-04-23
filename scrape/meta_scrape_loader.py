import pandas as pd
import requests
from bs4 import BeautifulSoup
from time import sleep
from .utils import url_to_filename
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import random


class MetaScrapeLoader:
    def __init__(self, df: pd.DataFrame, cache_dir: str):
        self.df = df
        self.cache_dir = cache_dir
    
    def load_nature(self):
        return self._load("nature.com", False, parse_page_nature)
    
    def load_ieee(self):
        return self._load("ieeexplore.ieee.org", True, parse_page_ieee)
    
    def load_jmlr(self):
        return self._load("jmlr.org", False, parse_page_jmlr)
    
    def load_neurips(self):
        return self._load("nips.cc", False, parse_page_neurips)
    
    def load_springer(self):
        return self._load("springer.com", False, parse_page_springer)
    
    def load_acm(self):
        return self._load("acm.org", True, parse_page_acm)
    
    def load_sciencedirect(self):
        return self._load("sciencedirect.com", True, parse_page_sciencedirect)

    def load_manual(self):
        # filter the df which does not contain http
        filtered_df = self.df[~self.df["link"].str.contains("http")].copy()

        # use link as summary
        filtered_df["summary"] = filtered_df["link"]
        return filtered_df


    def _load(self, site: str, dynamic_content: False, parse_func):
        # find all the records where Link contains "nature.com"
        filtered_df = self.df[self.df["link"].str.contains(site)].copy()

        for index, row in filtered_df.iterrows():
            url = row["link"]

            # check if ends with .pdf
            if url.endswith(".pdf"):
                print(f"Skipping {url} because it ends with .pdf")
                continue

            filename = url_to_filename(url)
            filename = os.path.join(self.cache_dir, filename)

            page = None
            if os.path.exists(filename):
                print(f"Loading {url} from cache")
                with open(filename, "r") as f:
                    page = f.read()
            else:
                if dynamic_content:
                    page = get_dynamic_content_and_abstract(url)
                else:
                    page = self.download_page(url)
                if page is None:
                    print(f"Failed to download paper: {url}")
                    continue
                sleep(3)
                with open(filename, "w") as f:
                    f.write(page)

            content = parse_func(page)
            if content is None:
                print(f"Failed to parse paper: {url}")
                continue
            filtered_df.at[index, 'summary'] = content

        return filtered_df

    def download_page(self, url: str):
        # set headers to mimic a browser
        print(f"Downloading {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to download, status code: {response.status_code}")
            return None
        return response.text


def parse_page_nature(page: str):
    soup = BeautifulSoup(page, "html.parser")
    # find id Abs1-content and get the child <p> content if not found, try Abs2-content
    div = soup.find(id="Abs1-content")
    if div is None:
        div = soup.find(id="Abs2-content")
    if div is None:
        div = soup.find(id="Abs3-content")
    if div is None:
        div = soup.find(id="Abs4-content")
    return div.text

def get_dynamic_content_and_abstract(url):
    user_agents = [
        'Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0'
    ]
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'user-agent={random.choice(user_agents)}')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        print(f"Downloading {url}")
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        page  = driver.page_source

    except Exception as e:
        print(f"Error getting dynamic content and abstract: {e}")
        return None
    finally:
        print("Downloading completed")
        driver.quit()

    return page

def parse_page_ieee(page: str):
    # Parse with BeautifulSoup
    soup = BeautifulSoup(page, 'html.parser')
    
    # Find meta tag with property "twitter:description"
    meta_tag = soup.find('meta', {'property': 'twitter:description'})
    if meta_tag:
        return meta_tag['content']
    return None

def parse_page_jmlr(page: str):
    soup = BeautifulSoup(page, 'html.parser')
    # find the node with class "abstract-text"
    div = soup.find(class_="abstract")
    return div.text

def parse_page_neurips(page: str):
    soup = BeautifulSoup(page, 'html.parser')
    # find the node with class "abstract-text"
    abstract_heading = soup.find('h4', text='Abstract')
    abstract_text = ""

    if abstract_heading:
        abstract_p = abstract_heading.find_next('p')
        while abstract_p:
            if abstract_p.text.strip():
                abstract_text += abstract_p.text
            abstract_p = abstract_p.find_next('p')
            if abstract_p and abstract_p.find_previous('h4') != abstract_heading:
                break
    if abstract_text.strip() == "":
        return None
    return abstract_text

def parse_page_springer(page: str):
    soup = BeautifulSoup(page, 'html.parser')
    # find the node with class "abstract-text"
    div = soup.find(id="Abs1-content")
    if div is None:
        return None
    # find all <p> tags
    p_tags = div.find_all('p')
    if len(p_tags) == 0:
        return None

    return " ".join([p.text for p in p_tags])

def parse_page_acm(page: str):
    soup = BeautifulSoup(page, 'html.parser')
    # find the node with role="paragraph"
    div = soup.find(role="paragraph")
    if div is None:
        return None
    return div.text



def parse_page_sciencedirect(page: str):
    soup = BeautifulSoup(page, 'html.parser')
    # find the node with class containing "aep-abstract-sec"
    div = soup.find(id=lambda x: x and "aep-abstract-sec" in x)
    if div is None:
        return None
    divs = div.find_all('div')
    if len(divs) == 0:
        return None
    return divs[0].text

