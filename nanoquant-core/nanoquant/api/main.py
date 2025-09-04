"""
NanoQuant API (Core Version)
Provides REST API access to model compression functionality without business logic
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NanoQuant Core API",
    description="Extreme LLM Compression Engine - Compress large language models by up to 99.5%",
    version="1.0.0"
)

class CompressionRequest(BaseModel):
    model_id: str
    compression_level: str = "medium"
    push_to_ollama: bool = True

class CompressionResponse(BaseModel):
    status: str
    message: str
    model_id: str
    compression_level: str
    ollama_tags: list

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "NanoQuant Core API - Compress LLMs into NanoQuants"}

@app.get("/compression-levels")
async def get_compression_levels():
    """Get available compression levels"""
    return {
        "light": {"name": "Light Compression", "description": "50-70% size reduction"},
        "medium": {"name": "Medium Compression", "description": "70-85% size reduction"},
        "heavy": {"name": "Heavy Compression", "description": "85-92% size reduction"},
        "extreme": {"name": "Extreme Compression", "description": "92-96% size reduction"},
        "ultra": {"name": "Ultra Compression", "description": "96-98% size reduction"},
        "nano": {"name": "Nano Compression", "description": "98-99% size reduction"},
        "atomic": {"name": "Atomic Compression", "description": "99-99.5% size reduction"}
    }

@app.post("/compress", response_model=CompressionResponse)
async def compress_model(request: CompressionRequest):
    """Compress a model into NanoQuant"""
    try:
        # Import the compression pipeline
        from nanoquant.core.compression_pipeline import CompressionPipeline
        
        # Create pipeline
        pipeline = CompressionPipeline()
        
        # Process model
        result = pipeline.process_model(
            model_id=request.model_id,
            compression_level=request.compression_level,
            push_to_ollama=request.push_to_ollama
        )
        
        return CompressionResponse(
            status="success",
            message="Model compressed successfully",
            model_id=request.model_id,
            compression_level=request.compression_level,
            ollama_tags=result.get("ollama_tags", [])
        )
    except Exception as e:
        logger.error(f"Compression error: {e}")
        return CompressionResponse(
            status="error",
            message=f"Compression failed: {str(e)}",
            model_id=request.model_id,
            compression_level=request.compression_level,
            ollama_tags=[]
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
