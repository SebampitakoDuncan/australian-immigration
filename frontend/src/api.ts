import axios from 'axios';
import { QueryRequest, QueryResponse, IngestResponse, SystemStats } from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for large file uploads
  maxContentLength: 100 * 1024 * 1024, // 100MB
  maxBodyLength: 100 * 1024 * 1024, // 100MB
});

export const ragApi = {
  // Query the RAG system
  async query(request: QueryRequest): Promise<QueryResponse> {
    const response = await api.post('/query', request);
    return response.data;
  },

  // Query with streaming response
  async queryStreaming(request: QueryRequest): Promise<ReadableStream<Uint8Array>> {
    const response = await fetch(`${API_BASE_URL}/query/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.body!;
  },

  // Upload and ingest a document
  async ingestDocument(
    file: File,
    source?: string,
    section?: string,
    docType?: string,
    onProgress?: (progress: number) => void
  ): Promise<IngestResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (source) formData.append('source', source);
    if (section) formData.append('section', section);
    if (docType) formData.append('doc_type', docType);

    const response = await api.post('/ingest', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });
    
    return response.data;
  },

  // Get system statistics
  async getSystemStats(): Promise<SystemStats> {
    const response = await api.get('/stats');
    return response.data;
  },

  // Test system components
  async testSystem(): Promise<any> {
    const response = await api.get('/test');
    return response.data;
  },

  // List documents
  async listDocuments(): Promise<any> {
    const response = await api.get('/documents');
    return response.data;
  },

  // Health check
  async healthCheck(): Promise<any> {
    const response = await api.get('/health');
    return response.data;
  },
};

