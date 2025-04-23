import os
from getpass import getpass

def URL():
    PASSWORD = os.getenv("VECTOR_DB_PWD")
    if PASSWORD is None:
        PASSWORD = getpass("Enter the password for the vector database: ")

    return f"postgresql://postgres:{PASSWORD}@smarttutor.eastus.azurecontainer.io:5432/postgres"

def OPENAI_API_KEY():
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if OPENAI_API_KEY is None:
        os.environ["OPENAI_API_KEY"] = getpass("Enter the OpenAI API key: ")