import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Generate embeddings for text chunks using sentence-transformers."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts."""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 64) -> np.ndarray:
        """Generate embeddings in batches to handle large datasets efficiently."""
        if self.model is None:
            raise RuntimeError("Model not loaded")

        if not texts:
            return np.array([])

        try:
            # Use larger batch size and optimize encoding parameters
            logger.info(f"Generating embeddings for {len(texts)} texts using batch_size={batch_size}")

            # Use optimized encoding parameters for speed
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False,  # Disable progress bar for speed
                convert_to_numpy=True,
                normalize_embeddings=True  # Normalize for better similarity
            )

            logger.info(f"Successfully generated embeddings with shape: {embeddings.shape}")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings batch: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings."""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        # Generate a dummy embedding to get the dimension
        dummy_embedding = self.generate_embedding("test")
        return len(dummy_embedding)
    
    def add_embeddings_to_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add embeddings to document chunks."""
        if not documents:
            return documents
        
        # Extract texts for batch processing
        texts = [doc["content"] for doc in documents]
        
        # Generate embeddings
        embeddings = self.generate_embeddings_batch(texts)
        
        # Add embeddings to documents
        for i, doc in enumerate(documents):
            doc["embedding"] = embeddings[i].tolist()
        
        return documents
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Compute cosine similarity between two embeddings."""
        # Normalize embeddings
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Compute cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        return float(similarity)
    
    def find_most_similar(self, query_embedding: np.ndarray, document_embeddings: List[np.ndarray], top_k: int = 5) -> List[tuple]:
        """Find the most similar documents to a query embedding."""
        similarities = []
        
        for i, doc_embedding in enumerate(document_embeddings):
            similarity = self.compute_similarity(query_embedding, doc_embedding)
            similarities.append((i, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
