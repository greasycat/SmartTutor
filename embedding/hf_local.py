from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

text = "This is a test document."
query_result = embeddings.embed_query(text)

# show only the first 100 characters of the stringified vector
print(str(query_result)[:100] + "...")