import os
import openai
import chromadb
import tiktoken
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_VERSION = os.getenv("API_VERSION")
API_ENDPOINT = os.getenv("API_ENDPOINT")
MODEL_EMBEDDING = os.getenv("MODEL_EMBEDDING")
DATA_FOLDER = "documents/"
CHROMA_DB_PATH = "./chroma_db"

if os.path.exists(CHROMA_DB_PATH):
    import shutil
    shutil.rmtree(CHROMA_DB_PATH)
    print("Existing ChromaDB dropped.")

chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = chroma_client.get_or_create_collection(name="document_embeddings")

client = openai.AzureOpenAI(
    azure_endpoint=API_ENDPOINT,
    api_key=API_KEY,
    api_version=API_VERSION
)

def count_tokens(text):
    encoder = tiktoken.get_encoding("cl100k_base")
    return len(encoder.encode(text))

def generate_embedding(text):
    response = client.embeddings.create(
        input=text,
        model=MODEL_EMBEDDING
    )
    return response.data[0].embedding

def process_document(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    
    token_count = count_tokens(text)
    print(f"{file_path} contains {token_count} tokens.")
    
    embedding = generate_embedding(text)
    collection.add(
        ids=[file_path],
        embeddings=[embedding],
        documents=[text]
    )
    print(f"{file_path} successfully stored as embedding!")

def process_all_files():
    if not os.path.exists(DATA_FOLDER):
        print(f"Data folder '{DATA_FOLDER}' not found.")
        return
    
    files = [f for f in os.listdir(DATA_FOLDER) if os.path.isfile(os.path.join(DATA_FOLDER, f))]
    if not files:
        print("No files found in the data folder.")
        return
    
    for file_name in files:
        file_path = os.path.join(DATA_FOLDER, file_name)
        print(f"Processing {file_name}...")
        process_document(file_path)

process_all_files()
