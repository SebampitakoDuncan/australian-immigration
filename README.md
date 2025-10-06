# Australian Immigration Law RAG System

A full-stack Retrieval-Augmented Generation (RAG) application for Australian immigration law queries, powered by gpt-oss-20b and ChromaDB.

## 🚀 Railway Deployment

### Prerequisites
- Railway account (https://railway.app)
- GitHub account
- Hugging Face API token
- Git installed locally

### Step 1: Prepare Your Repository
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit: Australian Immigration Law RAG System"

# Create GitHub repository and push
# (Replace with your GitHub username/repo)
git remote add origin https://github.com/yourusername/australian-immigration-rag.git
git push -u origin main
```

### Step 2: Create Railway Project
1. Go to https://railway.app and sign up/login
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account and select your repository

### Step 2: Deploy Backend Service
1. Railway will automatically detect the `railway.json` and `Dockerfile.backend`
2. Go to Variables tab in Railway dashboard
3. Add these environment variables:
   ```
   HF_TOKEN=your_huggingface_token_here
   CORS_ORIGINS=*
   CHROMA_PERSIST_DIRECTORY=/app/data/chroma_db
   DATA_DIR=/app/data
   DOCUMENTS_DIR=/app/data/immigration_docs
   ```

### Step 3: Deploy Frontend Service
1. In Railway dashboard, click "New" → "Service"
2. Select "Empty Service"
3. Choose "Add a Dockerfile" and select `Dockerfile.frontend`
4. In the frontend service Variables, add:
   ```
   VITE_API_URL=https://your-backend-service-name.up.railway.app/api
   ```
   (Replace with your actual backend service URL)

### Step 4: Configure Networking
1. In Railway dashboard, go to your frontend service
2. Click on "Settings" → "Domains"
3. Railway will provide a public URL for your frontend

### Step 5: Upload Initial Documents
1. Use the frontend interface to upload Australian immigration law documents
2. Or use the API directly to ingest documents

### Cost Estimate
- **Free Tier**: 512MB RAM, 1GB storage, 100 hours/month
- **When exceeded**: ~$5/month for backend, ~$0 for frontend (Railway static hosting)

### Troubleshooting
- Check Railway logs in the dashboard
- Ensure `HF_TOKEN` is set correctly
- Verify CORS settings if API calls fail
- Monitor memory usage for large document processing

## 🛠 Local Development

A production-ready RAG (Retrieval-Augmented Generation) system for querying Australian immigration law documents using OpenAI's gpt-oss-20b model. This demonstrates sovereign AI capabilities through practical question-answering on sensitive legal documents.

## 🚀 Features

- **Document Upload**: Upload PDF and text files containing Australian immigration law documents
- **Semantic Search**: Advanced retrieval using ChromaDB vector database
- **AI-Powered Answers**: Generate accurate responses using gpt-oss-20b via Hugging Face Inference API
- **Source Citations**: Every answer includes references to source documents
- **Real-time Interface**: Modern React + TypeScript frontend with streaming responses
- **Production Ready**: Docker containerized with Railway.app deployment support

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│  Frontend (React + TypeScript)          │
│  - Document upload interface            │
│  - Query interface with streaming       │
│  - Results display with citations       │
└────────────┬────────────────────────────┘
             │ HTTPS API calls
             ▼
┌─────────────────────────────────────────┐
│  Backend (FastAPI + Python)             │
│  - Document processing & chunking       │
│  - ChromaDB vector storage              │
│  - RAG pipeline orchestration           │
└────────────┬────────────────────────────┘
             │ API requests with HF_TOKEN
             ▼
┌─────────────────────────────────────────┐
│  Hugging Face Inference API             │
│  - gpt-oss-20b model (21B parameters)  │
│  - Mixture of Experts architecture      │
│  - Serverless, auto-scaling             │
└─────────────────────────────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **ChromaDB**: Vector database for semantic search
- **sentence-transformers**: Text embeddings
- **PyPDF2**: PDF text extraction
- **gpt-oss-20b**: OpenAI's open-weight model via Hugging Face

### Frontend
- **React 18**: Modern UI framework
- **TypeScript**: Type-safe development
- **TailwindCSS**: Utility-first styling
- **Vite**: Fast build tool
- **Axios**: HTTP client

### Deployment
- **Docker**: Containerization
- **Railway.app**: Cloud deployment platform
- **Nginx**: Reverse proxy and static file serving

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional)
- Hugging Face API token

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd showing
```

### 2. Set Up Environment Variables

```bash
cp env.example .env
```

Edit `.env` and add your Hugging Face API token:

```bash
HF_TOKEN=your_huggingface_token_here
```

### 3. Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 5. Using Docker (Alternative)

```bash
# Copy environment file
cp env.example .env

# Edit .env with your HF_TOKEN
# Then run:
docker-compose up --build
```

Access the application at `http://localhost`

## 📖 Usage

### 1. Upload Documents

1. Navigate to the "Upload Document" section
2. Select a PDF or text file containing Australian immigration law
3. Optionally add metadata (source, section, type)
4. Click "Upload Document"

The system will:
- Extract text from the document
- Split it into semantic chunks
- Generate embeddings
- Store in the vector database

### 2. Ask Questions

1. Type your question in the "Ask a Question" section
2. Optionally enable "Use advanced reranking" for better results
3. Click "Ask Question"

The system will:
- Retrieve relevant document chunks
- Generate an answer using gpt-oss-20b
- Display the answer with source citations

### Example Questions

- "What are the requirements for a partner visa?"
- "What is the character test under section 501?"
- "What are the conditions for a student visa?"
- "How does the refugee and humanitarian program work?"

## 🔧 API Endpoints

### Document Management
- `POST /api/ingest` - Upload and process documents
- `GET /api/documents` - List ingested documents

### Querying
- `POST /api/query` - Ask questions (standard response)
- `POST /api/query/stream` - Ask questions (streaming response)

### System
- `GET /api/health` - Health check
- `GET /api/stats` - System statistics
- `GET /api/test` - Test system components

## 🚀 Deployment on Railway.app

### 1. Prepare for Deployment

1. Push your code to GitHub
2. Ensure you have a Hugging Face API token

### 2. Deploy Backend

1. Go to [Railway.app](https://railway.app)
2. Create a new project
3. Connect your GitHub repository
4. Add environment variables:
   - `HF_TOKEN`: Your Hugging Face API token
   - `CORS_ORIGINS`: Your frontend URL
5. Deploy the backend service

### 3. Deploy Frontend

1. Create another service in Railway
2. Set the root directory to `/frontend`
3. Add environment variables:
   - `VITE_API_URL`: Your backend URL
4. Deploy the frontend service

### 4. Configure Domains

1. Add custom domains in Railway dashboard
2. Update CORS_ORIGINS in backend with your frontend domain

## 🔍 System Components

### Document Processing Pipeline

1. **Document Loader**: Extracts text from PDFs and text files
2. **Text Chunker**: Splits documents into semantic chunks (512 tokens with 50 token overlap)
3. **Embedding Generator**: Creates vector embeddings using sentence-transformers
4. **Vector Store**: Stores embeddings in ChromaDB for fast retrieval

### RAG Pipeline

1. **Query Processing**: Converts user questions to embeddings
2. **Retrieval**: Finds most relevant document chunks using semantic similarity
3. **Generation**: Uses gpt-oss-20b to generate answers with retrieved context
4. **Citation**: Returns source documents with each answer

### gpt-oss-20b Integration

- **Model**: OpenAI's gpt-oss-20b (21B parameters, MoE architecture)
- **API**: Hugging Face Inference API (serverless)
- **Features**: 
  - No local GPU required
  - Automatic scaling
  - Cost-effective inference
  - OpenAI-compatible API

## 📊 Performance & Monitoring

### System Statistics

The system provides real-time statistics:
- Total documents indexed
- Embedding dimensions
- Model information
- Configuration details

### Health Checks

- Backend health endpoint: `/api/health`
- Frontend health endpoint: `/health`
- Docker health checks configured

## 🔒 Security & Privacy

- **Data Sovereignty**: All processing happens in Australia-compatible infrastructure
- **API Security**: CORS configured for specific origins
- **Token Management**: Hugging Face tokens stored securely
- **Document Privacy**: Uploaded documents processed locally

## 🛠️ Development

### Project Structure

```
/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py              # Configuration
│   ├── rag/                   # RAG pipeline components
│   │   ├── document_loader.py
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── retriever.py
│   │   ├── generator.py
│   │   └── pipeline.py
│   ├── api/
│   │   └── routes.py          # API endpoints
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── types.ts          # TypeScript types
│   │   ├── api.ts            # API client
│   │   └── App.tsx           # Main app
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── README.md
```

### Adding New Features

1. **Backend**: Add new endpoints in `backend/api/routes.py`
2. **Frontend**: Create new components in `frontend/src/components/`
3. **RAG Pipeline**: Extend components in `backend/rag/`

## 🐛 Troubleshooting

### Common Issues

1. **HF_TOKEN not set**: Ensure your Hugging Face API token is correctly set
2. **CORS errors**: Check CORS_ORIGINS configuration
3. **Document upload fails**: Verify file format (PDF or TXT only)
4. **Slow responses**: Check Hugging Face API status

### Logs

- Backend logs: Available in Railway dashboard or Docker logs
- Frontend logs: Browser developer console
- System logs: Check `/api/test` endpoint for component status

## 📄 License

This project is a demonstration of sovereign AI capabilities for Australian immigration law.

## 🤝 Contributing

This is a demonstration project. For production use, consider:
- Adding authentication and authorization
- Implementing document versioning
- Adding more sophisticated chunking strategies
- Implementing caching for better performance
- Adding comprehensive error handling

## 📞 Support

For questions about this demonstration:
- Check the API documentation at `/docs` when running locally
- Review the system statistics at `/api/stats`
- Test system components at `/api/test`

