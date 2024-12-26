import asyncio
import streamlit as st
from core.document import DocumentProcessor
from core.retriever import Retriever
from core.chat import ChatManager
from utils.config import AppConfig
from utils.ui import UIManager
from utils.utils import setup_logging, generate_session_id
import requests

async def main():
    """
    Main function to run the Streamlit RAG application.
    """
    setup_logging()
    config = AppConfig()
    
    # Generate session ID
    session_id = generate_session_id()
    
    ui_manager = UIManager()
    ui_manager.display_main_title()
    ui_manager.add_custom_css()

    # Sidebar configuration
    chunk_size, chunk_overlap, vector_top_k, use_reranker, rerank_top_k, temperature, max_tokens = ui_manager.configure_sidebar()

    # Initialize document processor and retriever with session ID
    doc_processor = DocumentProcessor(config, chunk_size, chunk_overlap, session_id)
    retriever = Retriever(config, use_reranker, vector_top_k, rerank_top_k, session_id)

    # File upload and processing
    uploaded_file = ui_manager.display_file_upload_section()
    if uploaded_file:
        process_button = st.button("معالجة المستند", type="primary")
        if process_button:
            await doc_processor.process_and_store_embeddings(uploaded_file)

            if doc_processor.vectorstore:
                retriever.init_vectorstore(doc_processor.vectorstore)
                chat_manager = ChatManager(config, retriever, temperature, max_tokens, ui_manager)

                # Chat interface and handling
                ui_manager.display_chat_interface()
                chat_manager.handle_chat_input()

                # Display relevant context if available
                if st.session_state.chat_history:
                    ui_manager.display_relevant_context(retriever, st.session_state.chat_history[-1]['content'], use_reranker)
            else:
                st.error("Failed to initialize vector store. Please check the logs.")
        elif 'vectorstore' in st.session_state and st.session_state.vectorstore:
            # If documents were already processed, show chat interface
            retriever.init_vectorstore(st.session_state.vectorstore)
            chat_manager = ChatManager(config, retriever, temperature, max_tokens, ui_manager)
            chat_manager.handle_chat_input()
            ui_manager.display_chat_interface()

            if st.session_state.chat_history:
                ui_manager.display_relevant_context(retriever, st.session_state.chat_history[-1]['content'], use_reranker)
    else:
        ui_manager.display_info_message()


if __name__ == "__main__":
    asyncio.run(main())