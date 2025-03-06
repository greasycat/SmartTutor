import os
import re
import requests

class Downloader:
    def __init__(self, url: str, cache_dir: str):
        self.url = url
        self.cache_dir = cache_dir
        self.cache_filename = self.generate_cache_filename(url)


    def get(self) -> str:
        print(f"Downloading {self.url} to {self.cache_filename}")
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        file_path = os.path.join(self.cache_dir, self.cache_filename)

        if os.path.exists(file_path):
            print(f"Using cached file: {file_path}")
            with open(file_path, "r") as f:
                return f.read()
        # Download the file, enable redirects
        response = requests.get(self.url, allow_redirects=True)
        with open(file_path, "wb") as f:
            f.write(response.content)
        

    # replace all non-alphanumeric characters with underscores
    @staticmethod
    def generate_cache_filename(url: str):
        return re.sub(r'[^a-zA-Z0-9]', '_', url)
