import tempfile
import os
import fitz
from PIL import Image
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_pinecone import PineconeEmbeddings
from utils.utils import upload_image_to_fileio, extract_text_from_image_url, get_file_hash, generate_session_id
import logging
import streamlit as st
from core.embeddings import CustomEmbeddings

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Handles the processing of documents, including chunking and embedding storage.
    """
    def __init__(self, config, chunk_size, chunk_overlap, session_id: str = None):
        self.config = config
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            add_start_index=True
        )
        self.vectorstore = None
        self.file_hash = None
        self.session_id = session_id or generate_session_id()
        self.namespace = self.session_id

    def convert_pdf_to_images(self, pdf_path, output_folder, zoom=2):
        """
        Converts each page of a PDF file to a grayscale image and compresses it.
        """
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        images_paths = []
        try:
            doc = fitz.open(pdf_path)
            mat = fitz.Matrix(zoom, zoom)
            
            for i in range(len(doc)):
                image_path = os.path.join(output_folder, f"page_{i+1}.png")
                page = doc.load_page(i)
                pix = page.get_pixmap(matrix=mat)
                pix.save(image_path)
                
                image = Image.open(image_path).convert('L')
                compressed_image_path = os.path.join(output_folder, f"compressed_page_{i+1}.png")
                image.save(compressed_image_path, "PNG", optimize=True, quality=70)
                os.remove(image_path)
                
                images_paths.append(compressed_image_path)
                logger.info(f"Saved and compressed page {i+1} as image: {compressed_image_path}")
            
            doc.close()
            
        except Exception as e:
            logger.error(f"An error occurred while converting PDF to images: {e}")
        
        return images_paths
    
    def extract_text_from_pdf_or_image(self, file_path):
        """
        Extracts text from a PDF or an image file using OCR.
        """
        with tempfile.TemporaryDirectory() as temp_folder:
            if file_path.lower().endswith('.pdf'):
                image_paths = self.convert_pdf_to_images(file_path, temp_folder)
            else:
                image_paths = [file_path]

            combined_text = ""
            for image_path in image_paths:
                image_url = upload_image_to_fileio(image_path)
                if image_url:
                    page_text = extract_text_from_image_url(image_url)
                    combined_text += page_text + "\n\n"
                else:
                    logger.warning(f"Failed to upload or process image: {image_path}")

                if file_path.lower().endswith('.pdf'):
                    os.remove(image_path)
        # No need to manually remove files or the directory when using tempfile.TemporaryDirectory()
        return combined_text

    async def async_init_vectorstore(self, chunks):
        """
        Asynchronously initializes the Pinecone vector store with session namespace.
        """
        custom_embeddings = CustomEmbeddings(api_url="http://embedding:8000")
        vectorstore = PineconeVectorStore(
            index_name=self.config.PINECONE_INDEX_NAME,
            embedding=custom_embeddings,
            namespace=self.namespace,
            pinecone_api_key=self.config.PINECONE_API_KEY
        )
        vectorstore.add_documents(chunks)
        return vectorstore
    
    async def process_and_store_embeddings(self, uploaded_file):
        """
        Processes the uploaded file, creates document chunks, and stores embeddings.
        """
        current_file_hash = get_file_hash(uploaded_file.getvalue())

        if 'vectorstore' not in st.session_state or self.file_hash != current_file_hash:
            logger.info("New or changed file detected. Processing and storing embeddings.")

            with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as temp_file:
                temp_file.write(uploaded_file.getbuffer())
                temp_file_path = temp_file.name

            if uploaded_file.type == "text/plain":
                string_data = uploaded_file.getvalue().decode("utf-8")
            else:
                string_data = self.extract_text_from_pdf_or_image(temp_file_path)
            
            os.remove(temp_file_path)

            chunks = self.text_splitter.create_documents([string_data])

            # Display success message and document chunks
            st.markdown("""
                <div class="success-box" dir="rtl">
                    <strong>✅ تم تحميل المستند ومعالجته بنجاح!</strong>
                </div>
            """, unsafe_allow_html=True)

            with st.expander("📚 عرض قطع المستند"):
                for i, chunk in enumerate(chunks):
                    st.markdown(f"""
                        <div style="padding: 1rem; background-color: var(--background-color); border-radius: 5px; margin-bottom: 1rem; text-align: right;" dir="rtl">
                            <strong>🔹 القطعة {i+1}</strong> ({len(chunk.page_content)} حرف)<br>
                            <div style="margin-top: 0.5rem; padding: 1rem; background-color: #FFFFFF; border-radius: 5px;">
                                {chunk.page_content}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

            self.vectorstore = await self.async_init_vectorstore(chunks)
            st.session_state.vectorstore = self.vectorstore  # Store in session state
            self.file_hash = current_file_hash
            logger.info("Embeddings stored in vectorstore.")
        else:
            logger.info("File has not changed. Using existing vectorstore.")
            self.vectorstore = st.session_state.vectorstore