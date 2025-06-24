import os
import streamlit as st
from dotenv import load_dotenv
from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from classify import classify_risk
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

# Load key from .env (optional)
load_dotenv()
default_key = os.getenv("GOOGLE_API_KEY")

# Sidebar input for Gemini API key
st.sidebar.title("🔑 API Key Setup")
api_key = st.sidebar.text_input(
    "Enter your Google Gemini API key:",
    type="password",
    value=default_key if default_key else ""
)
st.sidebar.caption("🔒 Your key is only used in your browser session and sent securely to Gemini. It is never stored.")

# Stop the app if no key is provided
if not api_key:
    st.warning("Please enter your Google API key in the sidebar to continue.")
    st.stop()

# Set up Gemini + local embedding
llm = GoogleGenAI(model="gemini-2.5-flash", api_key=api_key)
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

Settings.llm = llm
Settings.embed_model = embed_model

# Load the vector index
persist_dir = "storage"

if not os.path.exists(persist_dir):
    # Rebuild index on Streamlit Cloud or fresh environment
    docs = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(docs)
    index.storage_context.persist(persist_dir=persist_dir)
else:
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    index = load_index_from_storage(storage_context)
    
query_engine = index.as_query_engine()

# Streamlit UI
st.set_page_config(page_title="PregniSense", layout="centered")
st.title("🤰 PregniSense - AI Pregnancy Risk Assistant")
st.markdown("This assistant helps evaluate pregnancy symptoms using AI + medical data. Always consult a healthcare provider for emergencies.")

# Questions
questions = [
    "Are you currently experiencing any unusual bleeding or discharge?",
    "How would you describe your baby’s movements today compared to yesterday?",
    "Have you had any headaches that won’t go away or that affect your vision?",
    "Do you feel any pressure or pain in your pelvis or lower back?",
    "Have you had a fever or noticed any foul-smelling discharge?"
]

user_inputs = []
for i, question in enumerate(questions):
    answer = st.text_input(question, key=f"q{i}")
    if answer:
        user_inputs.append(answer)

if st.button("Assess Risk") and user_inputs:
    combined_input = "\n".join(f"{q} {a}" for q, a in zip(questions, user_inputs))

    # RAG Query
    response = query_engine.query(combined_input)

    # Risk classification
    risk_level, advice = classify_risk(user_inputs)

    # Output
    st.subheader(f"🩺 Risk Level: {risk_level}")
    st.info(advice)

    # AI insight tucked away in an expander box
    with st.expander("Show AI-Powered Medical Insight"):
        st.write(response.response)

    st.caption("📌 This tool is for educational purposes. Please consult your doctor for medical decisions.")
