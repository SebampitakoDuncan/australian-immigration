from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import os

from .document_loader import DocumentLoader
from .chunking import TextChunker
from .embeddings import EmbeddingGenerator
from .vector_store import ChromaVectorStore
from .retriever import DocumentRetriever
from .generator import GPTOSSGenerator
from config import settings

logger = logging.getLogger(__name__)

class RAGPipeline:
    """End-to-end RAG pipeline for Australian immigration law."""
    
    def __init__(self):
        # Initialize components
        self.document_loader = DocumentLoader(settings.DOCUMENTS_DIR)
        self.text_chunker = TextChunker(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        self.embedding_generator = EmbeddingGenerator(settings.EMBEDDING_MODEL)
        self.vector_store = ChromaVectorStore(settings.CHROMA_PERSIST_DIRECTORY)
        self.retriever = DocumentRetriever(self.vector_store, self.embedding_generator)
        self.generator = GPTOSSGenerator(
            api_key=settings.HF_TOKEN,
            base_url=settings.HF_BASE_URL,
            model=settings.HF_MODEL
        )
        
        logger.info("RAG Pipeline initialized successfully")
    
    def ingest_document(self, file_path: str, filename: str, 
                       metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Ingest a single document into the RAG system."""
        try:
            # Add upload timestamp to metadata
            if metadata is None:
                metadata = {}
            metadata["upload_date"] = datetime.now().isoformat()
            
            # Process document based on file type
            if filename.lower().endswith('.pdf'):
                document = self.document_loader.process_uploaded_pdf(file_path, filename, metadata)
            elif filename.lower().endswith('.txt'):
                document = self.document_loader.process_uploaded_text_file(file_path, filename, metadata)
            else:
                raise ValueError(f"Unsupported file type: {filename}")
            
            # Chunk the document using fast strategy for better performance
            chunks = self.text_chunker.chunk_document(document, strategy="fast")
            
            # Generate embeddings for chunks
            chunks_with_embeddings = self.embedding_generator.add_embeddings_to_documents(chunks)
            
            # Store in vector database
            success = self.vector_store.add_documents(chunks_with_embeddings)
            
            if success:
                result = {
                    "status": "success",
                    "document_id": document["id"],
                    "title": document["title"],
                    "chunks_created": len(chunks),
                    "filename": filename,
                    "metadata": document["metadata"]
                }
                logger.info(f"Successfully ingested document: {filename}")
                return result
            else:
                raise Exception("Failed to store document in vector database")
                
        except Exception as e:
            logger.error(f"Error ingesting document {filename}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "filename": filename
            }
    
    def query(self, question: str, top_k: int = None, 
              use_reranking: bool = False) -> Dict[str, Any]:
        """Query the RAG system with a question."""
        try:
            if top_k is None:
                top_k = settings.TOP_K_RESULTS
            
            # Retrieve relevant documents
            if use_reranking:
                retrieved_docs = self.retriever.retrieve_with_reranking(question, top_k)
            else:
                retrieved_docs = self.retriever.retrieve_documents(question, top_k)
            
            if not retrieved_docs:
                return {
                    "status": "error",
                    "error": "No relevant documents found",
                    "question": question
                }
            
            # Generate response using gpt-oss-20b
            response = self.generator.generate_response(
                question=question,
                context_chunks=retrieved_docs,
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE
            )
            
            # Prepare final result
            result = {
                "status": "success",
                "question": question,
                "answer": response["answer"],
                "sources": [
                    {
                        "id": doc["id"],
                        "title": doc["metadata"].get("title", "Unknown"),
                        "source": doc["metadata"].get("source", "Unknown"),
                        "section": doc["metadata"].get("section", "Unknown"),
                        "similarity": doc.get("similarity", 0.0),
                        "content_preview": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"]
                    }
                    for doc in retrieved_docs
                ],
                "metadata": {
                    "retrieval_method": "reranking" if use_reranking else "semantic_search",
                    "documents_retrieved": len(retrieved_docs),
                    "generation_metadata": response["metadata"]
                }
            }
            
            logger.info(f"Successfully processed query: {question[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "status": "error",
                "error": str(e),
                "question": question
            }
    
    def query_streaming(self, question: str, top_k: int = None):
        """Query the RAG system with streaming response."""
        try:
            if top_k is None:
                top_k = settings.TOP_K_RESULTS
            
            # Retrieve relevant documents
            retrieved_docs = self.retriever.retrieve_documents(question, top_k)
            
            if not retrieved_docs:
                yield {"error": "No relevant documents found"}
                return
            
            # Generate streaming response
            for chunk in self.generator.generate_streaming_response(
                question=question,
                context_chunks=retrieved_docs,
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE
            ):
                yield {"chunk": chunk}
            
            # Send sources after completion
            yield {
                "sources": [
                    {
                        "id": doc["id"],
                        "title": doc["metadata"].get("title", "Unknown"),
                        "source": doc["metadata"].get("source", "Unknown"),
                        "section": doc["metadata"].get("section", "Unknown"),
                        "similarity": doc.get("similarity", 0.0)
                    }
                    for doc in retrieved_docs
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in streaming query: {e}")
            yield {"error": str(e)}
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        try:
            vector_store_stats = self.vector_store.get_collection_stats()
            retrieval_stats = self.retriever.get_retrieval_stats()
            model_info = self.generator.get_model_info()
            
            return {
                "vector_store": vector_store_stats,
                "retrieval": retrieval_stats,
                "generator": model_info,
                "pipeline_config": {
                    "chunk_size": settings.CHUNK_SIZE,
                    "chunk_overlap": settings.CHUNK_OVERLAP,
                    "top_k_results": settings.TOP_K_RESULTS,
                    "max_tokens": settings.MAX_TOKENS,
                    "temperature": settings.TEMPERATURE
                }
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {"error": str(e)}
    
    def test_system(self) -> Dict[str, Any]:
        """Test all components of the RAG system."""
        results = {}
        
        # Test vector store
        try:
            stats = self.vector_store.get_collection_stats()
            results["vector_store"] = {"status": "ok", "stats": stats}
        except Exception as e:
            results["vector_store"] = {"status": "error", "error": str(e)}
        
        # Test embedding generator
        try:
            test_embedding = self.embedding_generator.generate_embedding("test")
            results["embedding_generator"] = {"status": "ok", "dimension": len(test_embedding)}
        except Exception as e:
            results["embedding_generator"] = {"status": "error", "error": str(e)}
        
        # Test generator
        try:
            connection_ok = self.generator.test_connection()
            results["generator"] = {"status": "ok" if connection_ok else "error"}
        except Exception as e:
            results["generator"] = {"status": "error", "error": str(e)}
        
        return results
