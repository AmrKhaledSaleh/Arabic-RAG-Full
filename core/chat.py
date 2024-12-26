from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from datetime import datetime
import streamlit as st

class ChatManager:
    """
    Manages the chat interaction, model integration, and response generation.
    """
    def __init__(self, config, retriever, temperature, max_tokens, ui_manager):
        self.config = config
        self.retriever = retriever
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = 0.8
        self.ui_manager = ui_manager
        
        self.model = ChatGroq(
            model="llama-3.3-70b-specdec",
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=self.top_p,
            groq_api_key=self.config.GROQ_API_KEY,
            streaming=True
        )
        self.prompt = ChatPromptTemplate.from_template(
            """
            Answer the question based only on the following context.
            If the context does not provide enough information, respond with "الملفات اللي رفعتها مفيهاش إجابة سؤالك، بس انا هحاول أجاوب من عندي 🥸" and answer by yourself without context.
            Context:
            {context}

            Question:
            {question}
            """
        )

    def handle_chat_input(self):
        """
        Handles user input, retrieves relevant documents, generates a response,
        and updates the chat history.
        """
        question = st.chat_input("Ask about the documents:", key="chat_input_field")
        if question:
            st.session_state.chat_history.append({
                'role': 'user',
                'content': question,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            # self.ui_manager.display_chat_message(st.session_state.chat_history[-1])

            with st.chat_message("assistant"):
                # stream_handler = self.ui_manager.StreamHandler(st.empty())
                # self.model.callbacks = [stream_handler]
                chain = (
                    {
                        "context": RunnableLambda(self.retriever.invoke),
                        "question": RunnablePassthrough()
                    }
                    | self.prompt
                    | self.model
                    | StrOutputParser()
                )
                with st.spinner("جارٍ إنشاء الإجابة..."):
                    answer = chain.invoke(question)

                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': answer,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.caption(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))