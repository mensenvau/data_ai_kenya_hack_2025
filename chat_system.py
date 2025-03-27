import os
import openai
import chromadb
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_VERSION = os.getenv("API_VERSION")
API_ENDPOINT = os.getenv("API_ENDPOINT")
MODEL_EMBEDDING = os.getenv("MODEL_EMBEDDING")
MODEL_CHAT = os.getenv("MODEL_CHAT")

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="document_embeddings")

client = openai.AzureOpenAI(
    azure_endpoint=API_ENDPOINT,
    api_key=API_KEY,
    api_version=API_VERSION
)

def generate_query_embedding(user_query):
    response = client.embeddings.create(
        input=user_query,
        model=MODEL_EMBEDDING
    )
    return response.data[0].embedding

def retrieve_relevant_context(user_query):
    query_embedding = generate_query_embedding(user_query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    return " ".join(results["documents"][0]) if results["documents"] else "No relevant data found."

def get_openai_response(user_query):
    relevant_docs = retrieve_relevant_context(user_query)
    print(relevant_docs)

    response = client.chat.completions.create(
        model=MODEL_CHAT,
        messages=[
            {"role": "system", "content": 
             """You are the support of the online store asaxiy.uz, please answer only the following questions.
                📌 **Rules:**
                ✅ Provide only the necessary information.
                ✅ Do not ask unnecessary questions.
                ✅ Speak in the language chosen by the client.
                ✅ Try to get a phone number, but do not ask directly."""
            },
            {"role": "user",  "content": f"""Context: {relevant_docs} \nQuery: {user_query}""" }
        ]
    )
    return response.choices[0].message.content

user_input = "Can I return a product?"
print(get_openai_response(user_input))