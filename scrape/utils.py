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

def clean_text_for_embedding(text):
    # Convert to lowercase
    text = text.lower()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    
    # Remove , in numbers
    text = re.sub(r'(\d),(\d)', r'\1\2', text)

    
    # Handle \text{}
    text = re.sub(r'\\text\{([^\}]*?)\}', lambda match: f" {match.group(1).strip()} ", text)
    
    # Handle variants like \textrm, \textit, \textbf
    text_variants = ['textrm', 'textit', 'textbf', 'texttt', 'textsf']
    for variant in text_variants:
        text = re.sub(rf'\\{variant}\{{([^\}}]*?)\}}', 
                     lambda m: f"[{variant.upper()}]{m.group(1).strip()}[/{variant.upper()}]", 
                     text)

    # text = re.sub(r'\$([^\$]+?)\$', r' [INLINE_MATH]\1[/INLINE_MATH] ', text)
    # text = re.sub(r'\\\(\s*(.*?)\\s*\)', r' [INLINE_MATH]\1[/INLINE_MATH] ', text)

    # Replace special characters with space
    text = re.sub(r'[^\w\s]', ' ', text)

    # Remove extra spaces again
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text