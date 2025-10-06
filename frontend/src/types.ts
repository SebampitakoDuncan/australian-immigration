export interface QueryRequest {
  question: string;
  top_k?: number;
  use_reranking?: boolean;
}

export interface QueryResponse {
  status: string;
  question: string;
  answer?: string;
  sources?: Source[];
  metadata?: {
    retrieval_method: string;
    documents_retrieved: number;
    generation_metadata: {
      model: string;
      latency_seconds: number;
      tokens_used?: number;
    };
  };
  error?: string;
}

export interface Source {
  id: string;
  title: string;
  source: string;
  section: string;
  similarity: number;
  content_preview: string;
}

export interface IngestResponse {
  status: string;
  document_id?: string;
  title?: string;
  chunks_created?: number;
  filename?: string;
  metadata?: {
    source: string;
    section: string;
    type: string;
    title: string;
    filename: string;
    upload_date?: string;
    file_size: number;
  };
  error?: string;
}

export interface SystemStats {
  vector_store: {
    total_documents: number;
    collection_name: string;
    persist_directory: string;
  };
  retrieval: {
    vector_store_stats: any;
    embedding_model: string;
    embedding_dimension: number;
    retrieval_methods: string[];
  };
  generator: {
    model: string;
    base_url: string;
    api_type: string;
    description: string;
  };
  pipeline_config: {
    chunk_size: number;
    chunk_overlap: number;
    top_k_results: number;
    max_tokens: number;
    temperature: number;
  };
}

