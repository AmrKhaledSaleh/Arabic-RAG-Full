import streamlit as st
from langchain.callbacks.base import BaseCallbackHandler

class UIManager:
    """
    Manages the Streamlit UI components and interactions.
    """
    def __init__(self):
        self.init_session_state()

    def init_session_state(self):
        """Initializes the session state variables if they don't exist."""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'file_hash' not in st.session_state:
            st.session_state.file_hash = None
        if 'vectorstore' not in st.session_state:
            st.session_state.vectorstore = None

    def add_custom_css(self):
        """Adds custom CSS styles to the Streamlit app."""
        st.markdown("""
            <style>
            /* General Body Styles */
            body {
                font-family: 'Scheherazade', 'Amiri', serif; /* Arabic-style font */
                background-color: #f8f8f8; /* Soft background */
                color: #2c3e50; /* Darker text for contrast */
            }

            /* Title Container */
            .title-container {
                background-color: #2E5077;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            
            /* Chat Container */
            .chat-container {
                background-color: #F4EDD3;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.15);
                margin-bottom: 25px;
                direction: rtl; /* Set text direction to right-to-left */
            }

            /* Titles and Headers */
            .main-title {
                color: #F6F4F0; /* Gold color for elegance */
                text-align: center;
                margin-bottom: 20px;
                font-size: 2.5em;
                font-weight: bold;
                text-shadow: 2px 2px 3px rgba(0,0,0,0.2);
            }

            .subtitle {
                text-align: center;
                margin-bottom: 30px;
                color: #7f8c8d; /* Soft gray */
                font-size: 1.2em;
            }

            /* Sidebar Styling */
            .sidebar .sidebar-content {
                background-color: #f0f0f0; /* Light gray */
                padding: 20px;
                border-radius: 10px;
                box-shadow: 3px 3px 5px rgba(0,0,0,0.1);
            }

            .sidebar .stButton>button {
                background-color: #b29700; /* Gold color */
                color: white;
                border: none;
                width: 100%;
                padding: 10px 20px;
                border-radius: 25px; /* Rounded buttons */
                margin-bottom: 10px;
                font-weight: bold;
                box-shadow: 2px 2px 4px rgba(0,0,0,0.2);
                transition: all 0.3s ease; /* Smooth transition for hover effect */
            }

            .sidebar .stButton>button:hover {
                background-color: #9e8600; /* Darker gold on hover */
                box-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }

            .sidebar-footer {
                margin-top: 30px;
                font-size: 0.9em;
                color: #7f8c8d;
                text-align: center;
            }

            /* Chat Messages */
            .message {
                padding: 12px;
                margin-bottom: 15px;
                border-radius: 10px;
                color: white;
                font-weight: 500;
            }

            .user {
                background-color: #b29700; /* Gold for user */
            }

            .assistant {
                background-color: #7f8c8d; /* Soft gray for assistant */
            }

            .content {
                margin-bottom: 8px;
            }

            .timestamp {
                font-size: 0.7em;
                color: #ddd;
                text-align: right;
            }

            /* Input and Button Styles */
            .question-container {
                display: flex;
                gap: 15px;
                margin-bottom: 25px;
                justify-content: right;
            }

            .stTextInput>div>div>input {
                border-radius: 25px; /* Rounded input field */
                padding: 12px;
                border: 1px solid #b29700;
                text-align: right;
                box-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            }

            .ask-button-container .stButton>button {
                background-color: #27ae60; /* Green for action */
                color: white;
                border: none;
                border-radius: 25px;
                padding: 12px 25px;
                font-weight: bold;
                box-shadow: 2px 2px 4px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
            }

            .ask-button-container .stButton>button:hover {
                background-color: #219653; /* Darker green on hover */
                box-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }

            /* File Upload Container */
            .upload-container {
                background-color: #f0f0f0;
                padding: 25px;
                border-radius: 15px;
                margin-bottom: 25px;
                box-shadow: 3px 3px 5px rgba(0,0,0,0.1);
            }

            .upload-container .stFileUploader>div>div>div>input {
                border: 2px solid #b29700;
                border-radius: 10px;
            }

            /* Success and Info Boxes */
            .success-box, .info-box {
                padding: 18px;
                border-radius: 10px;
                margin-bottom: 25px;
                color: white;
                font-weight: 500;
            }

            .success-box {
                background-color: #27ae60;
            }

            .info-box {
                background-color: #2980b9;
            }

            /* Expander Styling */
            .st-expander {
                background-color: #f8f8f8;
                border: 2px solid #b29700;
                border-radius: 10px;
                margin-bottom: 20px;
            }

            .st-expander .st-expanderHeader {
                padding: 15px;
                font-weight: bold;
                color: #b29700;
            }

            .st-expander .st-expanderContent {
                padding: 15px;
            }

            /* Slider Styling */
            .stSlider .st-b8 { /* Track */
                background-color: #d3d3d3;
            }

            .stSlider .st-b9 { /* Thumb */
                background-color: #b29700;
            }

            .stSlider .st-b7:focus { /* Thumb on focus */
                box-shadow: 0 0 0 0.2rem rgba(178, 151, 0, 0.25);
            }

            .stSlider .st-b7:active { /* Thumb on active */
                background-color: #9e8600;
            }

            .stSlider .st-b9:hover { /* Thumb on hover */
                background-color: #9e8600;
            }
            </style>
        """, unsafe_allow_html=True)

    def display_main_title(self):
        """Displays the main title of the application."""
        st.markdown("""
            <div class="title-container" dir="rtl">
                <h1 class="main-title">🌟 Arabic RAG 🌟</h1>
                <p class="subtitle">Made with ❤️ by Amr Khaled</p>
            </div>
        """, unsafe_allow_html=True)

    # Sidebar for settings and configurations
    def configure_sidebar(self):
        with st.sidebar:
            st.markdown("<div dir='rtl'><h2>⚙️ الإعدادات</h2></div>", unsafe_allow_html=True)

            # Document Chunking Section
            st.markdown("<div dir='rtl'><h3>📄 تجزئة المستند</h3></div>", unsafe_allow_html=True)
            with st.expander("🔧 إعدادات التجزئة", expanded=True):
                chunk_size = st.slider("حجم القطعة", min_value=100, max_value=2000, value=512, help="عدد الأحرف لكل قطعة")
                chunk_overlap = st.slider("تداخل القطع", min_value=0, max_value=500, value=50, help="عدد الأحرف المتداخلة بين القطع")

            # Retrieval Settings Section
            st.markdown("<div dir='rtl'><h3>🔍 إعدادات الاسترجاع</h3></div>", unsafe_allow_html=True)
            with st.expander("🔧 تهيئة البحث", expanded=True):
                vector_top_k = st.slider("نتائج بحث المتجهات", min_value=1, max_value=20, value=4, help="عدد المستندات المراد استرجاعها من بحث المتجهات")
                use_reranker = st.checkbox("تمكين إعادة الترتيب", value=False, help="تبديل لتمكين/تعطيل إعادة الترتيب")
                if use_reranker:
                    rerank_top_k = st.slider("النتائج المعاد ترتيبها", min_value=1, max_value=vector_top_k, value=2, help="عدد المستندات المراد تحديدها بعد إعادة الترتيب")

            # Model Settings Section
            st.markdown("<div dir='rtl'><h3>🤖 إعدادات النموذج</h3></div>", unsafe_allow_html=True)
            with st.expander("🔧 تهيئة النموذج", expanded=True):
                temperature = st.slider("الحرارة", min_value=0.0, max_value=1.0, value=0.6, step=0.1, help="يتحكم في العشوائية في الإراج (0 = حتمي، 1 = إبداعي)")
                max_tokens = st.slider("أقصى عدد للرموز", min_value=256, max_value=4096, value=1024, step=256, help="أقصى عدد للرموز في الاستجابة")

            st.markdown("---")
            st.markdown('<div class="sidebar-footer" dir="rtl">مدعوم من Hams-AI<br>الإصدار 1.0</div>', unsafe_allow_html=True)
            if st.button("🔄 إعادة تعيين جميع الإعدادات"):
                self.reset_session_state()

        return chunk_size, chunk_overlap, vector_top_k, use_reranker, rerank_top_k if use_reranker else vector_top_k, temperature, max_tokens
    
    # Function to display the file upload section
    def display_file_upload_section(self):
        st.markdown('<div class="upload-container" dir="rtl">', unsafe_allow_html=True)
        st.markdown("<h2>📤 ارفع مستندك</h2>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("اختر ملف", type=["txt", "pdf", "png", "jpg", "jpeg"])
        st.markdown('</div>', unsafe_allow_html=True)
        return uploaded_file

    def display_chat_interface(self):
        """Displays the chat interface, including the chat history and input field."""
        st.markdown("<div dir='rtl'><h2>💬 المحادثة</h2></div>", unsafe_allow_html=True)
        st.markdown('<div class="chat-container" dir="rtl">', unsafe_allow_html=True)
        self.display_chat_history(st.session_state.chat_history)
        st.markdown('</div>', unsafe_allow_html=True)

    # Function to display chat messages with role, content, and timestamp
    def display_chat_message(self, message):
        """Displays a chat message with the appropriate styling."""
        user_icon = "https://static.vecteezy.com/system/resources/previews/008/442/086/original/illustration-of-human-icon-user-symbol-icon-modern-design-on-blank-background-free-vector.jpg"  # User icon URL
        assistant_icon = "https://static.vecteezy.com/system/resources/thumbnails/002/002/403/small/man-with-beard-avatar-character-isolated-icon-free-vector.jpg"  # Assistant icon URL

        if message['role'] == 'user':
            st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;" dir="ltr">
                    <div style="background-color: #b29700; color: white; padding: 10px; border-radius: 10px; max-width: 70%;">
                        <div style="text-align: right;" dir="rtl">{message['content']}</div>
                        <div style="text-align: right; font-size: 0.8em; color: #ddd;">{message['timestamp']}</div>
                    </div>
                    <img src="{user_icon}" style="width: 40px; height: 40px; border-radius: 50%; margin-left: 10px;">
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;" dir="ltr">
                    <img src="{assistant_icon}" style="width: 40px; height: 40px; border-radius: 50%; margin-right: 10px;">
                    <div style="background-color: #7f8c8d; color: white; padding: 10px; border-radius: 10px; max-width: 70%;">
                        <div style="text-align: left;" dir="rtl">{message['content']}</div>
                        <div style="text-align: left; font-size: 0.8em; color: #ddd;">{message['timestamp']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    def display_chat_history(self, chat_history):
        """
        Iterates through the chat history and displays each message.
        """
        for message in chat_history:
            self.display_chat_message(message)

    def display_relevant_context(self, retriever, question, use_reranker):
        """
        Retrieves and displays the relevant context from the vector store based on the user's question.
        """
        with st.expander("🔎 عرض السياق ذي الصلة"):
            relevant_docs = retriever.get_relevant_documents(question)
            for idx, doc in enumerate(relevant_docs, 1):
                st.markdown(f"""
                    <div style="padding: 1rem; background-color: var(--background-color); border-radius: 5px; margin-bottom: 1rem; text-align: right;" dir="rtl">
                        <strong>{'🔄 معاد ترتيبه' if use_reranker else '🔍 بحث المتجهات'} النتيجة {idx}</strong>
                        <div style="margin-top: 0.5rem; padding: 1rem; background-color: #FFFFFF; border-radius: 5px;">
                            {doc.page_content}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    def display_info_message(self):
        """Displays an informational message prompting the user to upload a file."""
        st.markdown("""
            <div class="info-box" dir="rtl">
                <strong>ℹ️ يرجى تحميل ملف نصي أو PDF أو صورة لبدء التحليل.</strong>
            </div>
        """, unsafe_allow_html=True)

    def reset_session_state(self):
        """Resets the session state variables and triggers a rerun of the Streamlit app."""
        st.session_state.chat_history = []
        st.session_state.file_hash = None
        st.session_state.vectorstore = None
        st.rerun()

    # Custom callback handler for streaming responses
    class StreamHandler(BaseCallbackHandler):
        def __init__(self, container, initial_text=""):
            self.container = container
            self.text = initial_text

        def on_llm_new_token(self, token: str, **kwargs) -> None:
            self.text += token
            self.container.markdown(self.text)

        def on_llm_end(self, *args, **kwargs) -> None:
            pass