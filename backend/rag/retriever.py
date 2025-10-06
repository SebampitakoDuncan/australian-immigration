from typing import List, Dict, Any, Optional
import logging
from .vector_store import ChromaVectorStore
from .embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)

class DocumentRetriever:
    """Retrieve relevant documents using semantic search."""
    
    def __init__(self, vector_store: ChromaVectorStore, embedding_generator: EmbeddingGenerator):
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
    
    def retrieve_documents(self, query: str, top_k: int = 5, 
                          filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Retrieve the most relevant documents for a query."""
        try:
            # Search using text (ChromaDB will handle embedding internally)
            results = self.vector_store.search_by_text(
                query_text=query,
                top_k=top_k,
                filter_metadata=filter_metadata
            )
            
            logger.info(f"Retrieved {len(results)} documents for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    def retrieve_documents_by_embedding(self, query_embedding: List[float], 
                                       top_k: int = 5, 
                                       filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Retrieve documents using a pre-computed query embedding."""
        try:
            results = self.vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k,
                filter_metadata=filter_metadata
            )
            
            logger.info(f"Retrieved {len(results)} documents using embedding")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving documents by embedding: {e}")
            return []
    
    def retrieve_with_reranking(self, query: str, top_k: int = 5, 
                               rerank_top_k: int = 10) -> List[Dict[str, Any]]:
        """Retrieve documents and rerank them for better relevance."""
        try:
            # First, get more documents than needed
            initial_results = self.retrieve_documents(query, top_k=rerank_top_k)
            
            if not initial_results:
                return []
            
            # Generate query embedding for reranking
            query_embedding = self.embedding_generator.generate_embedding(query)
            
            # Rerank based on embedding similarity
            reranked_results = []
            for result in initial_results:
                # Get document embedding (if available) or generate it
                if "embedding" in result:
                    doc_embedding = result["embedding"]
                else:
                    doc_embedding = self.embedding_generator.generate_embedding(result["content"])
                
                # Calculate similarity
                similarity = self.embedding_generator.compute_similarity(
                    query_embedding, doc_embedding
                )
                
                result["rerank_similarity"] = similarity
                reranked_results.append(result)
            
            # Sort by rerank similarity
            reranked_results.sort(key=lambda x: x["rerank_similarity"], reverse=True)
            
            # Return top k results
            final_results = reranked_results[:top_k]
            
            logger.info(f"Reranked and returned {len(final_results)} documents")
            return final_results
            
        except Exception as e:
            logger.error(f"Error in retrieve_with_reranking: {e}")
            return self.retrieve_documents(query, top_k)
    
    def retrieve_by_source(self, query: str, source: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve documents from a specific source."""
        filter_metadata = {"source": source}
        return self.retrieve_documents(query, top_k, filter_metadata)
    
    def retrieve_by_type(self, query: str, doc_type: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve documents of a specific type."""
        filter_metadata = {"type": doc_type}
        return self.retrieve_documents(query, top_k, filter_metadata)
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """Get statistics about the retrieval system."""
        try:
            vector_store_stats = self.vector_store.get_collection_stats()
            embedding_dim = self.embedding_generator.get_embedding_dimension()
            
            return {
                "vector_store_stats": vector_store_stats,
                "embedding_model": self.embedding_generator.model_name,
                "embedding_dimension": embedding_dim,
                "retrieval_methods": [
                    "semantic_search",
                    "embedding_search", 
                    "reranking",
                    "filtered_search"
                ]
            }
        except Exception as e:
            logger.error(f"Error getting retrieval stats: {e}")
            return {"error": str(e)}
