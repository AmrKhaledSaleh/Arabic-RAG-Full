from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from utils.utils import generate_session_id
import logging

logger = logging.getLogger(__name__)

class Retriever:
    """
    Retrieves relevant documents for a query, with optional reranking.
    """
    def __init__(self, config, use_reranker: bool, vector_top_k: int, rerank_top_k: int, session_id: str = None):
        self.config = config
        self.use_reranker = use_reranker
        self.vector_top_k = vector_top_k
        self.rerank_top_k = rerank_top_k
        self.vectorstore = None
        self.pc = Pinecone(api_key=self.config.PINECONE_API_KEY)
        self.index = self.pc.Index(self.config.PINECONE_INDEX_NAME)
        self.session_id = session_id or generate_session_id()
        self.namespace = self.session_id
        if self.use_reranker:
            self.reranker = self.pc.Index(self.config.PINECONE_INDEX_NAME)

    def init_vectorstore(self, vectorstore: PineconeVectorStore):
        """
        Initializes the vector store with the session-specific namespace.
        """
        self.vectorstore = vectorstore
        self.vectorstore._namespace = self.namespace

    def get_relevant_documents(self, query: str) -> list[Document]:
        """
        Retrieves relevant documents for a query from the session namespace.
        """
        if not self.vectorstore:
            logger.error("Vector store not initialized.")
            return []

        vector_results = self.vectorstore.similarity_search(
            query, 
            k=self.vector_top_k,
            namespace=self.namespace
        )

        if not self.use_reranker:
            return vector_results

        # Reranking logic
        docs_to_rerank = [doc.page_content for doc in vector_results]
        reranked_results = self.pc.inference.rerank(
            model="cohere-rerank-3.5",
            query=query,
            documents=docs_to_rerank,
            top_n=self.rerank_top_k,
            return_documents=True
        )

        reranked_docs = []
        for r in reranked_results.data:
            for doc in vector_results:
                if doc.page_content == r.document.text:
                    reranked_docs.append(doc)
                    break
        return reranked_docs

    def invoke(self, query: str) -> str:
        """
        Retrieves relevant documents and returns their concatenated content.
        """
        docs = self.get_relevant_documents(query)
        return "\n\n".join(doc.page_content for doc in docs)