import streamlit as st
import httpx
from uuid import uuid4

st.title("Assessment 2: Company-Specific RAG Chatbot")
st.caption("Strictly grounded • FAISS • Refusal logic • Confidence scoring")

if "session_id" not in st.session_state:
    st.session_state.session_id = uuid4()
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "confidence" in msg:
            st.caption(f"Confidence: {msg['confidence']:.3f}")

if prompt := st.chat_input("Ask anything about the company..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                resp = httpx.post(
                    "http://localhost:8000/api/02-rag/chat",
                    json={"query": prompt, "company_id": "acme-corp", "session_id": str(st.session_state.session_id)},
                    timeout=30,
                )
                if resp.status_code != 200:
                    # show full response when it's an error
                    st.error(f"API error ({resp.status_code}): {resp.text}")
                else:
                    data = resp.json()
                    try:
                        st.markdown(data["answer"])
                        st.caption(f"Confidence: {data['confidence']:.3f} | Sources: {', '.join(data['sources'])}")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": data["answer"],
                            "confidence": data["confidence"]
                        })
                    except KeyError:
                        st.error(f"Unexpected response format: {data}")
            except Exception as e:
                st.error(f"Error: {e}")