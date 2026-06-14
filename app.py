import streamlit as st

st.set_page_config(
page_title="Zyro Dynamics HR Assistant",
page_icon="🤖"
)

st.title("🤖 Zyro Dynamics HR Assistant")

st.write(
"Ask questions about Zyro Dynamics HR policies, leave, benefits, "
"performance reviews, onboarding, travel, and more."
)

# Initialize chat history

if some_condition:  # Line 17 (Whatever your if statement is)
    st.session_state.messages = []  # Line 18 (Indented with 4 spaces or 1 tab)

# Display chat history

for msg in st.session_state.messages:
with st.chat_message(msg["role"]):
st.markdown(msg["content"])

# User input

question = st.chat_input("Ask an HR question")

if question:

```
st.session_state.messages.append(
    {"role": "user", "content": question}
)

with st.chat_message("user"):
    st.markdown(question)

answer = (
    "This is a demo HR assistant. "
    "Connect your RAG pipeline here to answer questions "
    "from Zyro Dynamics policy documents."
)

with st.chat_message("assistant"):
    st.markdown(answer)

st.session_state.messages.append(
    {"role": "assistant", "content": answer}
)
```


