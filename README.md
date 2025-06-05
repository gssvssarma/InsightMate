🧠 InsightMate
InsightMate is your AI-powered knowledge and research companion, built with Streamlit and OpenRouter. It answers your questions using cutting-edge language models, while also leveraging your own knowledge base and web content for context-rich, accurate responses.

Features
Conversational Q&A: Ask anything and get intelligent, context-aware answers.
Persistent Memory: All your Q&A history is saved and restored automatically.
Knowledge Base: Upload your own .txt files to build a custom knowledge base. Select which files to use for each question.
Web Retrieval: Add content from any website to enhance the assistant’s responses.
Simple, Modern UI: Easy-to-use interface powered by Streamlit.

Usage
Install dependencies:
sh
pip install -r requirements.txt
Run the app:
sh
streamlit run InsightMate.py

Upload knowledge base files:
Use the sidebar to upload .txt files and select which to include as context.
Ask questions:
Enter your question in the main input box. The assistant will use your selected knowledge base files and any fetched website content to generate an answer.
Security Note
For production, store your API key securely (e.g., in environment variables or Streamlit secrets), not directly in the code.
License
MIT License
