import streamlit as st

st.set_page_config(page_title="Zyro Dynamics HR Assistant", page_icon="🤖")
st.title("🤖 Zyro Dynamics HR Assistant")

st.write(
    "Ask questions about Zyro Dynamics HR policies, leave, benefits, "
    "performance reviews, onboarding, travel, and more."
)

# Initialize chat history properly
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User input
question = st.chat_input("Ask an HR question")

if question:
    # 1. Add user message to history
    st.session_state.messages.append({"role": "user", "content": question})
    
    # 2. Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(question)
        
    # 3. Generate placeholder response
    answer = (
        "This is a demo HR assistant. "
        "Connect your RAG pipeline here to answer questions "
        "from Zyro Dynamics policy documents."
    )
    
    # 4. Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(answer)
        
    # 5. Add assistant message to history
    st.session_state.messages.append({"role": "assistant", "content": answer})


