from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import tempfile
import os
import logging
from datetime import datetime

from rag.pipeline import RAGPipeline
from config import settings

logger = logging.getLogger(__name__)

# Initialize RAG pipeline
rag_pipeline = RAGPipeline()

# Create router
router = APIRouter()

# Pydantic models
class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = None
    use_reranking: Optional[bool] = False

class QueryResponse(BaseModel):
    status: str
    question: str
    answer: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class IngestResponse(BaseModel):
    status: str
    document_id: Optional[str] = None
    title: Optional[str] = None
    chunks_created: Optional[int] = None
    filename: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class SystemStatsResponse(BaseModel):
    vector_store: Dict[str, Any]
    retrieval: Dict[str, Any]
    generator: Dict[str, Any]
    pipeline_config: Dict[str, Any]

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats():
    """Get comprehensive system statistics."""
    try:
        stats = rag_pipeline.get_system_stats()
        return SystemStatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test")
async def test_system():
    """Test all components of the RAG system."""
    try:
        test_results = rag_pipeline.test_system()
        return test_results
    except Exception as e:
        logger.error(f"Error testing system: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    source: Optional[str] = None,
    section: Optional[str] = None,
    doc_type: Optional[str] = None
):
    """Upload and ingest a document (PDF or text file). Supports files up to 100MB."""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.txt')):
            raise HTTPException(
                status_code=400, 
                detail="Only PDF and text files are supported"
            )
        
        # Check file size using configurable limit
        if file.size and file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB. Received: {file.size / (1024*1024):.1f}MB"
            )
        
        # Create temporary file with larger buffer for big files
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1], buffering=8192) as temp_file:
            # Write uploaded file to temporary file in chunks for large files
            content = await file.read()
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB. Received: {len(content) / (1024*1024):.1f}MB"
                )

            # Write in chunks for better memory management
            chunk_size = 8192
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i + chunk_size]
                temp_file.write(chunk)

            temp_file_path = temp_file.name
        
        try:
            # Prepare metadata
            metadata = {
                "source": source or "Uploaded Document",
                "section": section or "Unknown",
                "type": doc_type or "uploaded"
            }
            
            # Ingest document
            result = rag_pipeline.ingest_document(
                file_path=temp_file_path,
                filename=file.filename,
                metadata=metadata
            )
            
            return IngestResponse(**result)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query the RAG system with a question."""
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        result = rag_pipeline.query(
            question=request.question,
            top_k=request.top_k,
            use_reranking=request.use_reranking
        )
        
        return QueryResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query/stream")
async def query_documents_streaming(request: QueryRequest):
    """Query the RAG system with streaming response."""
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        def generate_stream():
            try:
                for chunk in rag_pipeline.query_streaming(
                    question=request.question,
                    top_k=request.top_k
                ):
                    yield f"data: {chunk}\n\n"
            except Exception as e:
                logger.error(f"Error in streaming query: {e}")
                yield f"data: {{'error': '{str(e)}'}}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting up streaming query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
async def list_documents():
    """List all ingested documents."""
    try:
        stats = rag_pipeline.get_system_stats()
        return {
            "total_documents": stats.get("vector_store", {}).get("total_documents", 0),
            "collection_name": stats.get("vector_store", {}).get("collection_name", "unknown")
        }
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a specific document."""
    try:
        # Note: This would require implementing delete functionality in the vector store
        # For now, return a not implemented response
        raise HTTPException(
            status_code=501, 
            detail="Document deletion not yet implemented"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))
