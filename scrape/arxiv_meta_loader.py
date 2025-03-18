import pandas as pd
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import os

class ArxivMetaLoader:
    def __init__(self, df: pd.DataFrame):
        # load all the records with Link contains arxiv.org
        self.df = df[df["Link"].str.contains("arxiv.org")]

        # split by / and get the last element
        self.df["arxiv_id"] = self.df["Link"].str.split("/").str[-1]

        # remove text after first v, this removes the version number
        self.df["arxiv_id"] = self.df["arxiv_id"].str.split("v").str[0]

        # remove .pdf or .html from the arxiv_id
        self.df["arxiv_id"] = self.df["arxiv_id"].str.replace(".pdf", "").str.replace(".html", "")

        # remove duplicates
        self.df = self.df.drop_duplicates(subset=["arxiv_id"])

        # reset the index
        self.df = self.df.reset_index(drop=True)

        self.ids = self.df["arxiv_id"].tolist()

        # trim space
        self.ids = [id.strip() for id in self.ids]

        # save the ids to a file
        with open("arxiv_ids.txt", "w") as f:
            for id in self.ids:
                f.write(id + "\n")
    
    def loads(self, meta_to_keep: list[str]):
        downloaded_df = self.apply()[["arxiv_id", *meta_to_keep]]

        # check if all the meta_to_keep are in the downloaded_df
        for meta in meta_to_keep:
            if meta not in downloaded_df.columns:
                raise ValueError(f"{meta} not in downloaded_df")

        # join the downloaded_df on arxiv_id
        self.df = self.df.merge(downloaded_df, on="arxiv_id", how="outer", indicator=True)

        # keep only the rows where the indicator is "both"
        df = self.df[self.df["_merge"] == "both"]

        # drop the _merge column
        df = df.drop(columns=["_merge"])

        # reset the index
        df = df.reset_index(drop=True)

        # print unmatched ids
        unmatched_ids = self.df[self.df["_merge"] == "left_only"]["arxiv_id"].tolist()
        print(f"Unmatched ids: {unmatched_ids}")


        return df


        






    def apply(self, cache="cache/arxiv_meta.xml"):
        if os.path.exists(cache):
            df = parse_arxiv_feed(open(cache, "r").read())
            return df

        url = f"https://arxiv.org/api/query?id_list={','.join(self.ids)}&max_results={len(self.ids)}"
        response = requests.get(url)
        if response.status_code == 200:
            with open(cache, "w") as f:
                f.write(response.text)
        else:
            print(f"Failed to download arxiv metas")
            print(response.text)
            return
        
        # parse the xml file
        df = parse_arxiv_feed(response.text)
        return df
    
    
def parse_arxiv_feed(xml_content):
    # Parse XML content
    root = ET.fromstring(xml_content)
    
    # Define namespaces
    namespaces = {
        'atom': 'http://www.w3.org/2005/Atom',
        'arxiv': 'http://arxiv.org/schemas/atom'
    }
    
    # Extract entries
    entries = root.findall('.//atom:entry', namespaces)
    
    records = []
    
    for entry in entries:
        # Extract basic metadata
        arxiv_id = entry.find('atom:id', namespaces).text.split('/')[-1]
        
        # Strip version info from arxiv_id (e.g., 1711.11053v2 -> 1711.11053)
        base_id = re.search(r'(\d+\.\d+)', arxiv_id).group(1) if re.search(r'(\d+\.\d+)', arxiv_id) else arxiv_id
        
        title = entry.find('atom:title', namespaces).text.strip()
        
        # Convert published and updated dates to datetime
        published = entry.find('atom:published', namespaces).text
        published_dt = datetime.strptime(published, '%Y-%m-%dT%H:%M:%SZ')
        
        updated = entry.find('atom:updated', namespaces).text
        updated_dt = datetime.strptime(updated, '%Y-%m-%dT%H:%M:%SZ')
        
        # Extract summary and remove extra whitespace
        summary_elem = entry.find('atom:summary', namespaces)
        summary = ' '.join(summary_elem.text.split()) if summary_elem is not None and summary_elem.text else ""
        
        # Extract authors (could be multiple)
        authors_elem = entry.findall('atom:author/atom:name', namespaces)
        authors = [author.text for author in authors_elem]
        authors_str = ', '.join(authors)
        
        # Extract primary category
        primary_category_elem = entry.find('arxiv:primary_category', namespaces)
        primary_category = primary_category_elem.get('term') if primary_category_elem is not None else ""
        
        # Extract all categories
        categories_elem = entry.findall('atom:category', namespaces)
        categories = [category.get('term') for category in categories_elem]
        categories_str = ', '.join(categories)
        
        # Extract comment if available
        comment_elem = entry.find('arxiv:comment', namespaces)
        comment = comment_elem.text if comment_elem is not None and comment_elem.text else ""
        
        # Extract links
        links = entry.findall('atom:link', namespaces)
        abstract_url = ""
        pdf_url = ""
        
        for link in links:
            rel = link.get('rel')
            href = link.get('href')
            
            if rel == 'alternate':
                abstract_url = href
            elif rel == 'related' and link.get('title') == 'pdf':
                pdf_url = href
        
        # Create a record dictionary
        record = {
            'arxiv_id': base_id,
            'version': arxiv_id.replace(base_id, '') if base_id in arxiv_id else "",
            'title': title,
            'published_date': published_dt,
            'updated_date': updated_dt,
            'summary': summary,
            'authors': authors_str,
            'primary_category': primary_category,
            'categories': categories_str,
            'comment': comment,
            'abstract_url': abstract_url,
            'pdf_url': pdf_url
        }
        
        records.append(record)
    
    # Create DataFrame
    df = pd.DataFrame(records)
    return df