import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from langchain_huggingface import HuggingFaceEmbeddings

app = FastAPI()

# Set up model cache directory
cache_dir = os.path.join(os.getcwd(), "model_cache")
os.makedirs(cache_dir, exist_ok=True)

# Initialize the embedding model
model = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-small",
    cache_folder=cache_dir,
    model_kwargs={'trust_remote_code': True}
)

class EmbeddingRequest(BaseModel):
    texts: List[str]

class EmbeddingResponse(BaseModel):
    embeddings: List[List[float]]

@app.post("/embed", response_model=EmbeddingResponse)
async def embed(request: EmbeddingRequest):
    try:
        embeddings = model.embed_documents(request.texts)
        return EmbeddingResponse(embeddings=embeddings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 