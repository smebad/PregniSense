import os
from dotenv import load_dotenv

# LlamaIndex components
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# for API key
load_dotenv()

# Model configuration
llm = GoogleGenAI(model="gemini-2.5-flash", api_key=os.getenv("GOOGLE_API_KEY"))

# Embedding Model
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Configuring LLM using global Settings
Settings.llm = llm
Settings.embed_model = embed_model

# Load the text files from the data folder
docs = SimpleDirectoryReader("data").load_data()

# Creating vector index for the documents
index = VectorStoreIndex.from_documents(docs)

# Save to disk
index.storage_context.persist(persist_dir="storage")
print("✅ Index built successfully with Gemini + local embeddings.")
