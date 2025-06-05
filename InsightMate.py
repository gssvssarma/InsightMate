import requests
import json

# Use your OpenRouter API key
api_key = "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"

# Select one of these models: 
# 'mistralai/mistral-7b-instruct', 'google/gemini-pro', 'anthropic/claude-3-haiku'
model = "anthropic/claude-3-haiku"

# General-purpose assistant context knowledge base
context_docs = [
    "You are InsightMate, an AI-powered assistant designed to help users with research, general knowledge, productivity, and learning tasks.",
    "Always provide clear, concise, and accurate answers. When appropriate, show step-by-step reasoning or examples.",
    "If you don't know the answer or it requires specialized expertise, say so honestly and suggest how to find out.",
    "Be friendly, professional, and respectful in all responses.",
    "You can answer questions on a wide range of topics including science, technology, history, language, productivity, and more.",
    "If a question is ambiguous, ask for clarification.",
    "Never provide harmful, unsafe, or unethical advice."
]

context = "\n".join(context_docs)

def ask_openrouter(user_input, extra_context=None):
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Compose context: base + website
    full_context = context
    if extra_context:
        full_context += "\n--- Website Content ---\n" + extra_context

    messages = [
        {"role": "system", "content": f"You are a helpful research assistant. Use the following context to answer questions:\n\n{full_context}"},
        {"role": "user", "content": user_input}
    ]

    data = {
        "model": model,
        "messages": messages
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        reply = response.json()['choices'][0]['message']['content']
        return reply.strip()
    else:
        return f"❌ Error {response.status_code}: {response.text}"

import streamlit as st
import os
import json
import requests
from urllib.parse import urlparse
import streamlit as st

MEMORY_FILE = "qa_memory.json"
KNOWLEDGE_BASE_DIR = "knowledge_base"
if not os.path.exists(KNOWLEDGE_BASE_DIR):
    os.makedirs(KNOWLEDGE_BASE_DIR)

st.set_page_config(page_title="InsightMate", page_icon="🧠")
st.title("🧠 InsightMate")
st.write("Your AI-powered knowledge and research companion. Powered by OpenRouter.")
st.warning("Your API key is hardcoded in the script. For production, use Streamlit secrets or environment variables.")

# --- Persistent Q&A Memory ---
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_memory(memory):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = load_memory()

# --- Knowledge Base: Upload and Select Text Files ---
def list_kb_files():
    return [f for f in os.listdir(KNOWLEDGE_BASE_DIR) if f.endswith('.txt')]

def read_kb_file(filename):
    with open(os.path.join(KNOWLEDGE_BASE_DIR, filename), 'r', encoding='utf-8') as f:
        return f.read()

st.sidebar.header("Knowledge Base")
with st.sidebar.expander("Upload Text Files (.txt)"):
    uploaded_files = st.file_uploader("Add .txt files to your knowledge base", type=["txt"], accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(KNOWLEDGE_BASE_DIR, uploaded_file.name)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(uploaded_file.read().decode('utf-8'))
        st.success("Uploaded successfully! Refresh the sidebar to see new files.")

kb_files = list_kb_files()
selected_kb_files = st.sidebar.multiselect("Select knowledge base files to use as context", kb_files, default=kb_files)

# --- Website Retrieval ---
if 'website_content' not in st.session_state:
    st.session_state['website_content'] = ""

with st.expander("Add Website Content to Assistant Context"):
    url = st.text_input("Enter website URL:", "")
    if st.button("Fetch Website"):
        if url:
            try:
                resp = requests.get(url)
                resp.raise_for_status()
                # Simple text extraction (for demo; for production, use BeautifulSoup or newspaper3k)
                text = resp.text
                st.session_state['website_content'] = text[:5000]  # Limit to 5000 chars
                st.success(f"Fetched content from {urlparse(url).netloc}")
            except Exception as e:
                st.session_state['website_content'] = ""
                st.error(f"Failed to fetch: {e}")

# --- User Q&A ---
# --- Compose knowledge base context ---
def get_kb_context(selected_files):
    kb_context = ""
    for fname in selected_files:
        content = read_kb_file(fname)
        kb_context += f"\n--- {fname} ---\n" + content[:3000]  # Limit per file
    return kb_context

user_input = st.text_input("Ask a question:", "")
if st.button("Ask"):
    if user_input.strip():
        with st.spinner("Thinking..."):
            kb_context = get_kb_context(selected_kb_files)
            combined_context = kb_context + "\n" + st.session_state['website_content']
            answer = ask_openrouter(user_input, extra_context=combined_context)
        st.session_state['chat_history'].append({"question": user_input, "answer": answer})
        save_memory(st.session_state['chat_history'])

# --- Show Q&A History ---
if st.session_state['chat_history']:
    st.subheader("Conversation History (Persistent)")
    for qa in reversed(st.session_state['chat_history']):
        st.markdown(f"**You:** {qa['question']}")
        st.markdown(f"**Assistant:** {qa['answer']}")
