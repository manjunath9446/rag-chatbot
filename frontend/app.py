import streamlit as st
import requests

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="HR Chatbot", page_icon="🤖", layout="wide")

# --- BACKEND API URLS ---
UPLOAD_URL = "http://backend:5000/upload"
QUERY_URL = "http://backend:5000/query"

# --- SIDEBAR FOR FILE UPLOAD ---
with st.sidebar:
    st.header("Upload Documents")
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
                    response = requests.post(UPLOAD_URL, files=files_to_send)
                    if response.status_code == 200:
                        st.success("Documents processed successfully! You can now ask questions.")
                        st.session_state.messages = [] # Clear chat history
                    else:
                        st.error(f"Error: {response.json().get('error')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: Could not connect to the backend. {e}")
        else:
            st.warning("Please upload at least one PDF file.")

# --- MAIN CHAT INTERFACE ---
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
            response = requests.post(QUERY_URL, json={"query": prompt})
            if response.status_code == 200:
                result = response.json()
                answer = result.get("answer", "I couldn't find an answer.")
                message_placeholder.markdown(answer)
                
                sources = result.get("sources", [])
                if sources:
                    with st.expander("View Sources"):
                        st.info("\n\n---\n\n".join(sources))
            else:
                error_msg = response.json().get('error')
                message_placeholder.error(f"Error: {error_msg}")

        except requests.exceptions.RequestException as e:
            message_placeholder.error(f"Connection error: Could not get a response from the backend. {e}")
