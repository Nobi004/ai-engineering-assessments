import streamlit as st
import httpx
import json

st.title("Assessment 1: AI Agent Workflow Automation (n8n-style)")
st.write("Send a lead → LLM intent + extraction + response (with retry & fallback)")

raw_input = st.text_area(
    "Lead JSON (or use the example)",
    value='{"name": "Alice Johnson", "email": "alice@acme.com", "message": "I want to discuss a partnership for our SaaS product"}',
    height=200,
)

if st.button("Process Lead"):
    with st.spinner("Processing with LLM..."):
        try:
            response = httpx.post(
                "http://localhost:8000/api/01-workflow/leads",
                json=json.loads(raw_input),
                timeout=30,
            )
            result = response.json()

            if response.status_code == 200:
                st.success("✅ Lead processed successfully!")
                st.json(result)
            else:
                st.error(f"Error {response.status_code}: {result}")
        except Exception as e:
            st.error(f"Connection error: {e}")