import os
import streamlit as st
from dotenv import load_dotenv
from llama_index.core import (StorageContext, load_index_from_storage, Settings, SimpleDirectoryReader, VectorStoreIndex)
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from classify import classify_risk

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

if not api_key:
    st.warning("Please enter your Google API key in the sidebar to continue.")
    st.stop()

# Setup Gemini + embedding
llm = GoogleGenAI(model="gemini-2.5-flash", api_key=api_key)
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
Settings.llm = llm
Settings.embed_model = embed_model

# Load or build the vector index
persist_dir = "storage"
if not os.path.exists(persist_dir):
    docs = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(docs)
    index.storage_context.persist(persist_dir=persist_dir)
else:
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    index = load_index_from_storage(storage_context)

query_engine = index.as_query_engine()

# Streamlit page config
st.set_page_config(page_title="PregniSense Chat", layout="centered")
st.title("🤰 PregniSense - AI Pregnancy Risk Assistant")
st.markdown("**Let's chat about your symptoms.**\nRespond step-by-step, and I’ll evaluate your risk level.")

# Initialize chat session state
if "history" not in st.session_state:
    st.session_state.history = []        # (role, message)
    st.session_state.answers = []        # User responses
    st.session_state.q_idx = 0           # Question index

questions = [
    "Are you currently experiencing any unusual bleeding or discharge?",
    "How would you describe your baby’s movements today compared to yesterday?",
    "Have you had any headaches that won’t go away or that affect your vision?",
    "Do you feel any pressure or pain in your pelvis or lower back?",
    "Have you had a fever or noticed any foul-smelling discharge?"
]

# Show chat history
for role, msg in st.session_state.history:
    st.chat_message(role).write(msg)

# Chat-style symptom collection
if st.session_state.q_idx < len(questions):
    if not st.session_state.history or st.session_state.history[-1][0] == "user": # If last message was from user, show next question
        question = questions[st.session_state.q_idx] # Get the next question
        st.session_state.history.append(("assistant", question)) # Add question to history
        st.rerun() # To display the question immediately


    user_input = st.chat_input("Your answer...")
    if user_input: # If user has entered an answer
        st.session_state.history.append(("user", user_input)) # Add user input to history
        st.session_state.answers.append(user_input) # Store the answer
        st.session_state.q_idx += 1 # Move to the next question
        st.rerun()


# Once all questions are answered
else:
    risk_level, advice = classify_risk(st.session_state.answers)  # Classify risk
    st.chat_message("assistant").write(f"🩺 Risk Level: **{risk_level}**\n\n{advice}")

    symptom_summary = "\n".join(
        f"{q} {a}" for q, a in zip(questions, st.session_state.answers)
    )

    custom_prompt = (
        "The following is a list of pregnancy symptoms reported by a patient. "
        "Please explain what these symptoms might medically indicate using the knowledge base, "
        "but do NOT provide any risk level or diagnostic judgment. Just explain what these symptoms suggest.\n\n"
        f"{symptom_summary}"
    )

    response = query_engine.query(custom_prompt)

    with st.expander("Show AI-Powered Medical Insight"):
        st.write(response.response)

    st.caption("📌 This tool is for educational purposes. Please consult your doctor for medical decisions.")
