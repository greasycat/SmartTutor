import re

def convert_model_name(model_name: str):
    # use regex to remove special characters except for _
    return re.sub(r'[^a-zA-Z0-9_]', '', model_name)