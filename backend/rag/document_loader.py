import os
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from pypdf import PdfReader
from pathlib import Path
import logging
import signal
import time

logger = logging.getLogger(__name__)

class DocumentLoader:
    """Load and process Australian immigration law documents from various sources."""

    def __init__(self, documents_dir: str):
        self.documents_dir = Path(documents_dir)
        self.documents_dir.mkdir(parents=True, exist_ok=True)

    def timeout_handler(self, signum, frame):
        """Handle timeout for long-running operations."""
        raise TimeoutError("Operation timed out")

    def load_pdf_with_timeout(self, file_path: str, timeout: int = 30) -> str:
        """Load text content from a PDF file with timeout using pypdf."""
        try:
            # Set up signal-based timeout (Unix only)
            if hasattr(signal, 'SIGALRM'):
                old_handler = signal.signal(signal.SIGALRM, self.timeout_handler)
                signal.alarm(timeout)

            # Use pypdf for faster PDF processing
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:  # Only add non-empty text
                    text += page_text + "\n"
            return text.strip()

        except TimeoutError:
            logger.error(f"PDF processing timed out after {timeout} seconds: {file_path}")
            return ""
        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {e}")
            return ""
        finally:
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
    
    def load_pdf(self, file_path: str) -> str:
        """Load text content from a PDF file with timeout protection."""
        return self.load_pdf_with_timeout(file_path, timeout=30)
    
    def load_text_file(self, file_path: str) -> str:
        """Load text content from a text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"Error loading text file {file_path}: {e}")
            return ""
    
    def scrape_web_page(self, url: str) -> str:
        """Scrape text content from a web page."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {e}")
            return ""
    
    def process_uploaded_pdf(self, file_path: str, filename: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process an uploaded PDF file and extract text content."""
        try:
            logger.info(f"Starting PDF processing for: {filename}")

            # Extract text from PDF with timeout
            content = self.load_pdf(file_path)

            if not content:
                logger.warning(f"No text content extracted from PDF: {filename}")
                raise ValueError("No text content extracted from PDF")

            logger.info(f"Successfully extracted {len(content)} characters from PDF: {filename}")

            # Generate document ID from filename
            doc_id = filename.replace('.pdf', '').replace(' ', '_').lower()

            # Create document structure
            document = {
                "id": doc_id,
                "title": filename.replace('.pdf', ''),
                "content": content,
                "source": metadata.get("source", "Uploaded Document") if metadata else "Uploaded Document",
                "section": metadata.get("section", "Unknown") if metadata else "Unknown",
                "type": metadata.get("type", "uploaded") if metadata else "uploaded",
                "filename": filename,
                "metadata": {
                    "source": metadata.get("source", "Uploaded Document") if metadata else "Uploaded Document",
                    "section": metadata.get("section", "Unknown") if metadata else "Unknown",
                    "type": metadata.get("type", "uploaded") if metadata else "uploaded",
                    "title": filename.replace('.pdf', ''),
                    "filename": filename,
                    "upload_date": metadata.get("upload_date") if metadata else None,
                    "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
                }
            }

            logger.info(f"Successfully processed PDF: {filename} ({len(content)} chars)")
            return document

        except Exception as e:
            logger.error(f"Error processing PDF {filename}: {e}")
            raise
    
    def process_uploaded_text_file(self, file_path: str, filename: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process an uploaded text file."""
        try:
            # Extract text from file
            content = self.load_text_file(file_path)
            
            if not content:
                raise ValueError("No text content found in file")
            
            # Generate document ID from filename
            doc_id = filename.replace('.txt', '').replace(' ', '_').lower()
            
            # Create document structure
            document = {
                "id": doc_id,
                "title": filename.replace('.txt', ''),
                "content": content,
                "source": metadata.get("source", "Uploaded Document") if metadata else "Uploaded Document",
                "section": metadata.get("section", "Unknown") if metadata else "Unknown",
                "type": metadata.get("type", "uploaded") if metadata else "uploaded",
                "filename": filename,
                "metadata": {
                    "source": metadata.get("source", "Uploaded Document") if metadata else "Uploaded Document",
                    "section": metadata.get("section", "Unknown") if metadata else "Unknown",
                    "type": metadata.get("type", "uploaded") if metadata else "uploaded",
                    "title": filename.replace('.txt', ''),
                    "filename": filename,
                    "upload_date": metadata.get("upload_date") if metadata else None,
                    "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
                }
            }
            
            logger.info(f"Successfully processed text file: {filename}")
            return document
            
        except Exception as e:
            logger.error(f"Error processing text file {filename}: {e}")
            raise
    
    def save_document(self, content: str, filename: str, metadata: Dict[str, Any] = None) -> str:
        """Save a document to the documents directory."""
        file_path = self.documents_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        if metadata:
            metadata_path = self.documents_dir / f"{filename}.metadata.json"
            import json
            with open(metadata_path, 'w', encoding='utf-8') as file:
                json.dump(metadata, file, indent=2)
        
        return str(file_path)
