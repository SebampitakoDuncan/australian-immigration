import tiktoken
from typing import List, Dict, Any
import re

class TextChunker:
    """Split documents into semantic chunks for RAG retrieval."""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in text."""
        return len(self.encoding.encode(text))
    
    def split_text_by_tokens(self, text: str) -> List[str]:
        """Split text into chunks based on token count."""
        tokens = self.encoding.encode(text)
        chunks = []
        
        start = 0
        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(tokens):
                break
        
        return chunks
    
    def split_text_by_sentences(self, text: str) -> List[str]:
        """Split text into chunks by sentences, respecting token limits."""
        # Split by sentences (simple approach)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # Check if adding this sentence would exceed chunk size
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if self.count_tokens(test_chunk) <= self.chunk_size:
                current_chunk = test_chunk
            else:
                # Save current chunk if it has content
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Start new chunk with current sentence
                if self.count_tokens(sentence) <= self.chunk_size:
                    current_chunk = sentence
                else:
                    # If single sentence is too long, split by tokens
                    token_chunks = self.split_text_by_tokens(sentence)
                    chunks.extend(token_chunks[:-1])  # Add all but last
                    current_chunk = token_chunks[-1]  # Start new chunk with last part
        
        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def split_text_by_paragraphs(self, text: str) -> List[str]:
        """Split text into chunks by paragraphs, respecting token limits."""
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Check if adding this paragraph would exceed chunk size
            test_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph
            
            if self.count_tokens(test_chunk) <= self.chunk_size:
                current_chunk = test_chunk
            else:
                # Save current chunk if it has content
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Start new chunk with current paragraph
                if self.count_tokens(paragraph) <= self.chunk_size:
                    current_chunk = paragraph
                else:
                    # If single paragraph is too long, split by sentences
                    sentence_chunks = self.split_text_by_sentences(paragraph)
                    chunks.extend(sentence_chunks[:-1])  # Add all but last
                    current_chunk = sentence_chunks[-1]  # Start new chunk with last part
        
        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def chunk_document(self, document: Dict[str, Any], strategy: str = "fast") -> List[Dict[str, Any]]:
        """Chunk a document using the specified strategy. 'fast' uses simple token-based chunking."""
        content = document["content"]
        metadata = document.get("metadata", {})

        if strategy == "fast":
            # Fast token-based chunking (simplified approach)
            chunks = self.split_text_by_tokens_fast(content)
        elif strategy == "tokens":
            chunks = self.split_text_by_tokens(content)
        elif strategy == "sentences":
            chunks = self.split_text_by_sentences(content)
        elif strategy == "paragraphs":
            chunks = self.split_text_by_paragraphs(content)
        else:
            raise ValueError(f"Unknown chunking strategy: {strategy}")

        # Create chunk documents with metadata
        chunk_documents = []
        for i, chunk_text in enumerate(chunks):
            chunk_doc = {
                "id": f"{document['id']}_chunk_{i}",
                "content": chunk_text,
                "metadata": {
                    **metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "parent_document_id": document["id"],
                    "parent_document_title": document.get("title", ""),
                    "token_count": self.count_tokens(chunk_text)
                }
            }
            chunk_documents.append(chunk_doc)

        return chunk_documents

    def split_text_by_tokens_fast(self, text: str) -> List[str]:
        """Fast token-based chunking without complex overlap handling."""
        tokens = self.encoding.encode(text)
        chunks = []

        for i in range(0, len(tokens), self.chunk_size):
            chunk_tokens = tokens[i:i + self.chunk_size]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)

        return chunks
    
    def chunk_documents(self, documents: List[Dict[str, Any]], strategy: str = "paragraphs") -> List[Dict[str, Any]]:
        """Chunk multiple documents."""
        all_chunks = []
        
        for document in documents:
            chunks = self.chunk_document(document, strategy)
            all_chunks.extend(chunks)
        
        return all_chunks
