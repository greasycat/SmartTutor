import re
from urllib.parse import urlparse
def url_to_filename(url):
    
    # Extract domain and path
    parsed = urlparse(url)
    base = parsed.netloc + parsed.path
    
    # Remove special characters, replace with underscores
    clean = re.sub(r'[^a-zA-Z0-9_.-]', '_', base)
    
    # Remove consecutive underscores
    clean = re.sub(r'_+', '_', clean)

    return clean