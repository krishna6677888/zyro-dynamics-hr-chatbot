import os
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader # Changed to PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# If the above still fails, ensure you are using the latest structural patterns
# documented for langchain-core and langchain-chains:
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# 1. Page Configuration
st.set_page_config(page_title="Zyro Dynamics HR Help Desk", page_icon="🤖", layout="wide")
st.title("🤖 Zyro Dynamics HR Help Desk")

# 2. Configure API Keys
from kaggle_secrets import UserSecretsClient
secrets = UserSecretsClient()
os.environ["GROQ_API_KEY"] = secrets.get_secret("Hr related") # Ensure this label matches your Kaggle Secret
os.environ["LANGCHAIN_API_KEY"] = secrets.get_secret("langchain Hr")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "zyro-rag-challenge"

# 3. Initialize RAG Pipeline
@st.cache_resource
def initialize_rag():
    pdf_dir = "/kaggle/input/competitions/niat-masterclass-rag-challenge/zyro-dynamics-hr-corpus/"
    all_documents = []
    
    # Load all PDFs from the specific competition path
    for filename in sorted(os.listdir(pdf_dir)):
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(pdf_dir, filename))
            all_documents.extend(loader.load())
            
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    final_docs = text_splitter.split_documents(all_documents)
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.from_documents(final_docs, embeddings)
    # Using MMR as requested in the challenge for better results
    return vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 4, "fetch_k": 10})

retriever = initialize_rag()

# 4. Chat logic
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question := st.chat_input("Ask an HR-related question..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        llm = ChatGroq(model="llama-3.3-70b-versatile") # Updated model
        
        system_prompt = (
            "You are an HR assistant for Zyro Dynamics. Answer the user's question "
            "using ONLY the provided context. If the question is out of scope or "
            "not in the context, reply exactly with: "
            "'I can only answer HR-related questions from Zyro Dynamics policy documents.'\n\n"
            "Context:\n{context}"
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
        
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        
        with st.spinner("Reviewing policies..."):
            response = rag_chain.invoke({"input": question})
            answer = response["answer"]
            st.markdown(answer)
                
    st.session_state.messages.append({"role": "assistant", "content": answer})
