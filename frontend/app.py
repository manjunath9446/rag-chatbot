import streamlit as st
import requests
import os
import json

st.set_page_config(page_title="HR Chatbot", page_icon="🤖", layout="wide")

BACKEND_URL = os.getenv("BACKEND_API_URL", "http://backend:5000")
UPLOAD_URL = f"{BACKEND_URL}/upload"
QUERY_URL = f"{BACKEND_URL}/query"

with st.sidebar:
    st.header("Upload Documents")
    st.info("Note: The first time you process a document, the server may take up to a minute to wake up.")
    
    uploaded_files = st.file_uploader(
        "Upload your HR policy PDF files here",
        type="pdf",
        accept_multiple_files=True
    )

    if st.button("Process Documents"):
        if uploaded_files:
            files_to_send = [("files", (file.name, file.getvalue(), file.type)) for file in uploaded_files]
            with st.spinner("Processing documents... This may take a moment."):
                try:
                    response = requests.post(UPLOAD_URL, files=files_to_send, timeout=60) # Add a timeout
                    if response.status_code == 200:
                        st.success("Documents processed successfully! You can now ask questions.")
                        st.session_state.messages = []
                    else:
                        st.error(f"Error processing documents. Server responded with: {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: Could not connect to the backend. It might be starting up. Please try again in a moment. Details: {e}")
        else:
            st.warning("Please upload at least one PDF file.")

st.title("HR Policy Chatbot 🤖")
st.write("Upload your HR documents in the sidebar, process them, and then ask me anything!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about the uploaded policies"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            response = requests.post(QUERY_URL, json={"query": prompt}, timeout=60) # Add a timeout
            if response.status_code == 200:
                result = response.json()
                answer = result.get("answer", "I couldn't find an answer.")
                message_placeholder.markdown(answer)

                sources = result.get("sources", [])
                if sources:
                    with st.expander("View Sources"):
                        st.info("\n\n---\n\n".join(sources))
            else:
                message_placeholder.error(f"Error querying. Server responded with: {response.text}")

        except requests.exceptions.RequestException as e:
            message_placeholder.error(f"Connection error: Could not get a response. Please try again. Details: {e}")