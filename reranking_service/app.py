import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

app = FastAPI()

# Set up model cache directory
cache_dir = os.path.join(os.getcwd(), "model_cache/NAMAA-Space_GATE-Reranker-V1")

# Initialize the reranking model
model = HuggingFaceCrossEncoder(
    model_name=cache_dir,
    model_kwargs={'trust_remote_code': True}
)

class RerankerRequest(BaseModel):
    query: str
    documents: List[str]
    top_k: int

class ScoredDocument(BaseModel):
    text: str
    score: float

class RerankerResponse(BaseModel):
    results: List[ScoredDocument]

@app.post("/rerank", response_model=RerankerResponse)
async def rerank(request: RerankerRequest):
    try:
        # Get similarity scores for each document
        scores = model.predict([(request.query, doc) for doc in request.documents])
        
        # Create scored documents
        scored_docs = [
            ScoredDocument(text=doc, score=float(score))
            for doc, score in zip(request.documents, scores)
        ]
        
        # Sort by score and take top_k
        sorted_docs = sorted(scored_docs, key=lambda x: x.score, reverse=True)[:request.top_k]
        
        return RerankerResponse(results=sorted_docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 