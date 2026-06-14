import streamlit as st

st.set_page_config(
    page_title="Zyro Dynamics HR Help Desk",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Zyro Dynamics HR Help Desk")

st.markdown("""
Welcome to the AI-powered HR Assistant for **Zyro Dynamics**.

You can ask questions about:

* Leave Policy
* Work From Home Policy
* Compensation & Benefits
* Performance Reviews
* Travel & Expense Policy
* Employee Handbook
* Onboarding & Separation
* IT & Data Security
* POSH Policy
""")

# Sidebar
with st.sidebar:
    st.header("About")
    st.write(
        "This chatbot is built using Retrieval-Augmented Generation (RAG) "
        "to answer HR-related questions from Zyro Dynamics policy documents."
    )

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
question = st.chat_input("Ask an HR-related question...")

if question:
    # 1. Add user message to history
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    # 2. Display user message
    with st.chat_message("user"):
        st.markdown(question)

    # 3. Generate response string
    answer = """
I am the Zyro Dynamics HR Assistant.

This Streamlit deployment is active. Connect your RAG pipeline
to provide document-grounded HR answers with citations.
"""

    # 4. Display assistant response
    with st.chat_message("assistant"):
        st.markdown(answer)

    # 5. Add assistant message to history
    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

