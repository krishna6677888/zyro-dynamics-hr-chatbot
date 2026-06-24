import os
import streamlit as st
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# 1. Page Configuration
st.set_page_config(
    page_title="Zyro Dynamics HR Help Desk",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Zyro Dynamics HR Help Desk")

# 2. Configure API Keys & Environment
try:
    # Try Kaggle Secrets first
    from kaggle_secrets import UserSecretsClient
    secrets = UserSecretsClient()
    os.environ["GROQ_API_KEY"] = secrets.get_secret("Hr related")
    os.environ["LANGCHAIN_API_KEY"] = secrets.get_secret("langchain Hr")
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "zyro-rag-challenge"
except Exception:
    # Fallback to Streamlit Cloud Secrets
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
        os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = "zyro-rag-challenge"
    else:
        # Local development fallback
        from dotenv import load_dotenv
        load_dotenv()

# 3. Initialize RAG Pipeline (Cached so it runs once)
@st.cache_resource
def initialize_rag():
    # Make sure your PDFs are inside a folder named 'policies' in your GitHub repo!
    if not os.path.exists("policies"):
        os.makedirs("policies")
        
    loader = PyPDFDirectoryLoader("policies/")
    docs = loader.load()
    
    if not docs:
        return None
        
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    final_docs = text_splitter.split_documents(docs)
    
    # Using a free HuggingFace model for local embeddings generation
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.from_documents(final_docs, embeddings)
    return vector_store.as_retriever(search_kwargs={"k": 3})

retriever = initialize_rag()

# 4. Sidebar Welcome Information
with st.sidebar:
    st.header("About")
    st.write(
        "This chatbot is built using Retrieval-Augmented Generation (RAG) "
        "to answer HR-related questions from Zyro Dynamics policy documents."
    )
    if retriever is None:
        st.warning("⚠️ No PDFs found in the 'policies/' directory. Please upload files to look up data.")

st.markdown("""
Welcome to the AI-powered HR Assistant for **Zyro Dynamics**.
You can ask questions about company policies like Leave, WFH, POSH, and Compensation.
""")

# 5. Maintain Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Handle User Query Interaction
question = st.chat_input("Ask an HR-related question...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        if retriever is None:
            answer = "I cannot search for answers because no PDF documents have been uploaded to my backend system yet."
            st.markdown(answer)
        else:
            try:
                # Initializing Groq Llama model via LangChain
                llm = ChatGroq(model="llama3-8b-8192")
                
                system_prompt = (
                    "You are an HR assistant for Zyro Dynamics. Answer the user's question "
                    "using only the provided context. If you don't know the answer based on "
                    "the context, kindly state that you cannot find it in the current policy guidelines.\n\n"
                    "Context:\n{context}"
                )
                prompt = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    ("human", "{input}"),
                ])
                
                question_answer_chain = create_stuff_documents_chain(llm, prompt)
                rag_chain = create_retrieval_chain(retriever, question_answer_chain)
                
                # Run pipeline
                with st.spinner("Reviewing policies..."):
                    response = rag_chain.invoke({"input": question})
                    answer = response["answer"]
                    st.markdown(answer)
            except Exception as e:
                answer = f"An execution error occurred while processing your request: {str(e)}"
                st.error(answer)
                
    st.session_state.messages.append({"role": "assistant", "content": answer})
