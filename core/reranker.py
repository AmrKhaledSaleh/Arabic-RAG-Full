import requests
from typing import List
from dataclasses import dataclass

@dataclass
class RankedDocument:
    text: str
    score: float

class CustomReranker:
    def __init__(self, api_url: str):
        self.api_url = api_url

    def rerank(self, query: str, documents: List[str], top_k: int) -> List[RankedDocument]:
        response = requests.post(
            f"{self.api_url}/rerank",
            json={
                "query": query,
                "documents": documents,
                "top_k": top_k
            }
        )
        response.raise_for_status()
        return [
            RankedDocument(**result) 
            for result in response.json()["results"]
        ] 