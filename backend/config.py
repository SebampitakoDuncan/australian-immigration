import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Hugging Face API
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    HF_BASE_URL: str = "https://router.huggingface.co/v1"
    HF_MODEL: str = "openai/gpt-oss-20b"

    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma_db")

    # API Settings
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "512"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # File Upload Settings
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
    MAX_FILE_SIZE: int = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes

    # RAG Settings
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "512"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))

    # Embedding Model (faster alternative for production)
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"  # Can be changed to "sentence-transformers/paraphrase-MiniLM-L3-v2" for faster processing

    # Data paths
    DATA_DIR: str = os.getenv("DATA_DIR", "./data")
    DOCUMENTS_DIR: str = os.path.join(DATA_DIR, "immigration_docs")

settings = Settings()
