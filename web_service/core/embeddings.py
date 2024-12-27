import requests
from typing import List
from langchain_core.embeddings import Embeddings

class CustomEmbeddings(Embeddings):
    def __init__(self, api_url: str):
        self.api_url = api_url

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        response = requests.post(
            f"{self.api_url}/embed",
            json={"texts": texts}
        )
        response.raise_for_status()
        return response.json()["embeddings"]

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0] 