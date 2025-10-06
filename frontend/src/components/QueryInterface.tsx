import React, { useState } from 'react';
import { FileText, Settings, User, Bot, Clock, Database, Brain, CheckCircle, AlertCircle } from 'lucide-react';
import { ragApi } from '../api';
import { QueryRequest, QueryResponse, IngestResponse, Source } from '../types';

interface QueryInterfaceProps {
  queryResult: QueryResponse | null;
  loading: boolean;
  onQueryResult: (result: QueryResponse) => void;
  onLoading: (loading: boolean) => void;
}

export const QueryInterface: React.FC<QueryInterfaceProps> = ({ queryResult, loading, onQueryResult, onLoading }) => {
  const [question, setQuestion] = useState('');
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadResult, setUploadResult] = useState<IngestResponse | null>(null);
  const [fileSizeError, setFileSizeError] = useState<string | null>(null);

  // Function to render HTML content safely from backend
  const formatAnswer = (text: string) => {
    if (!text) return '';

    // Check if the text contains HTML tags (processed by backend markdown)
    if (text.includes('<') && text.includes('>') && (text.includes('<p>') || text.includes('<strong>') || text.includes('<em>') || text.includes('<br>'))) {
      // Render as HTML with proper styling
      return (
        <div
          className="prose prose-slate max-w-none text-slate-800 leading-relaxed [&_strong]:font-semibold [&_strong]:text-slate-900 [&_em]:italic [&_em]:text-slate-700 [&_ul]:list-disc [&_ul]:ml-4 [&_ol]:list-decimal [&_ol]:ml-4 [&_li]:mb-1 [&_code]:bg-slate-100 [&_code]:px-1 [&_code]:py-0.5 [&_code]:rounded [&_code]:text-sm [&_code]:font-mono [&_blockquote]:border-l-4 [&_blockquote]:border-slate-300 [&_blockquote]:pl-4 [&_blockquote]:italic [&_*]:font-['Inter'] [&_p]:font-['Inter'] [&_div]:font-['Inter'] [&_span]:font-['Inter'] [&_strong]:font-['Inter'] [&_em]:font-['Inter'] [&_li]:font-['Inter'] [&_blockquote]:font-['Inter']"
          dangerouslySetInnerHTML={{ __html: text }}
        />
      );
    }

    // Fallback: treat as plain text
    return (
      <div className="text-slate-800 leading-relaxed whitespace-pre-wrap">
        {text}
      </div>
    );
  };


  const SourceCard: React.FC<{ source: Source; index: number }> = ({ source, index }) => {
    const similarityPercentage = Math.round(source.similarity * 100);

    return (
      <div className="bg-white border border-slate-200 rounded-lg p-3 shadow-sm mb-2">
        <div className="flex items-start justify-between mb-1">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-medium text-primary-600">#{index}</span>
              <h4 className="font-medium text-slate-900 text-sm truncate">
                {source.title}
              </h4>
            </div>
            <div className="text-xs text-slate-600 mb-1">
              <span className="font-medium">{source.source}</span>
              {source.section && source.section !== 'Unknown' && (
                <> • {source.section}</>
              )}
            </div>
            <div className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
              similarityPercentage >= 80
                ? 'bg-emerald-100 text-emerald-800'
                : similarityPercentage >= 60
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-slate-100 text-slate-700'
            }`}>
              <CheckCircle className="h-3 w-3" />
              {similarityPercentage}% relevant
            </div>
          </div>
        </div>
        <div className="text-xs text-slate-700 line-clamp-2 mt-2">
          {source.content_preview}
        </div>
      </div>
    );
  };

  const handleQuery = async () => {
    if (!question.trim()) return;

    onLoading(true);
    try {
      const request: QueryRequest = {
        question: question.trim(),
      };

      const result = await ragApi.query(request);
      onQueryResult(result);
    } catch (error) {
      console.error('Query error:', error);
      onQueryResult({
        status: 'error',
        question: question,
        error: 'Failed to process query. Please try again.',
      });
    } finally {
      onLoading(false);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) {
      setUploadFile(null);
      setFileSizeError(null);
      return;
    }

    // Check file size (100MB limit)
    const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB
    if (file.size > MAX_FILE_SIZE) {
      setFileSizeError(`File too large. Maximum size is 100MB. Selected file: ${(file.size / (1024 * 1024)).toFixed(1)}MB`);
      setUploadFile(null);
      return;
    }

    setFileSizeError(null);
    setUploadFile(file);
    setUploadResult(null);

    // Automatically upload the file when selected
    await handleFileUpload(file);
  };

  const handleFileUpload = async (selectedFile?: File) => {
    const fileToUpload = selectedFile || uploadFile;
    if (!fileToUpload) return;

    setUploadLoading(true);
    setUploadProgress(0);
    setUploadResult(null);

    try {
      const result = await ragApi.ingestDocument(
        fileToUpload,
        undefined, // No source
        undefined, // No section
        'uploaded', // Default doc type
        setUploadProgress
      );
      setUploadResult(result);

      if (result.status === 'success') {
        // Show 100% progress on success
        setUploadProgress(100);
        // Keep loading state for a moment to show completion
        setTimeout(() => {
          setUploadLoading(false);
          setUploadProgress(0);
          // Reset form but keep the uploaded document for reference
          setFileSizeError(null);
        }, 1500); // Show success for 1.5 seconds
      } else {
        setUploadLoading(false);
        setUploadProgress(0);
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadResult({
        status: 'error',
        error: 'Failed to upload document. Please try again.',
      });
      setUploadLoading(false);
      setUploadProgress(0);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleQuery();
    }
  };

  return (
    <div className="space-y-6">
      {/* Query Input Section */}
      <div className="card">
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Ask a Question</h2>
        </div>

        <div className="space-y-6">
          {/* Document Upload */}
          <div>
            <label htmlFor="file-upload" className="block text-sm font-medium text-gray-700 mb-3">
              Upload Document (Optional - PDF or Text, Max 100MB)
            </label>
            <input
              id="file-upload"
              type="file"
              accept=".pdf,.txt"
              onChange={handleFileSelect}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
            />

            {uploadFile && (
              <div className="mt-2 text-sm text-gray-600">
                Selected: {uploadFile.name} ({(uploadFile.size / (1024 * 1024)).toFixed(1)}MB)
              </div>
            )}
            {fileSizeError && (
              <div className="mt-2 text-sm text-red-600">
                {fileSizeError}
              </div>
            )}

            {(uploadLoading || uploadProgress === 100) && (
              <div className="mt-3">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${
                      uploadProgress === 100 ? 'bg-green-500' : 'bg-primary-600'
                    }`}
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
                <div className="flex items-center justify-center mt-2 text-green-600 text-sm font-medium">
                  <CheckCircle className="w-4 h-4 mr-1" />
                  {uploadProgress === 100 ? 'Document uploaded successfully!' : 'Uploading...'}
                </div>
              </div>
            )}
          </div>

          {/* Question Input */}
          <div>
            <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
              Your Question
            </label>
            <textarea
              id="question"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="e.g., What are the requirements for a partner visa?"
              className="input-field min-h-[100px] resize-none"
              rows={4}
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end">
            <button
              onClick={handleQuery}
              disabled={!question.trim()}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Ask Question
            </button>
          </div>
        </div>
      </div>

      {/* Chat Conversation Section */}
      {(loading || queryResult) && (
        <div className="card">
          <div className="flex items-center gap-2 mb-6">
            <Bot className="h-5 w-5 text-primary-600" />
            <h2 className="text-xl font-semibold text-gray-900">Conversation</h2>
          </div>

          <div className="space-y-6">
            {/* User's Question */}
            {queryResult && (
              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                    <User className="h-5 w-5 text-primary-700" />
                  </div>
                </div>
                <div className="flex-1">
                  <div className="bg-primary-50 border border-primary-200 rounded-2xl rounded-tl-md px-4 py-3">
                    <p className="text-primary-900 font-medium">You</p>
                    <p className="text-primary-800 mt-1">{queryResult.question}</p>
                  </div>
                </div>
              </div>
            )}

            {/* AI Response */}
            {loading ? (
              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-slate-100 rounded-full flex items-center justify-center">
                    <Bot className="h-5 w-5 text-slate-700" />
                  </div>
                </div>
                <div className="flex-1">
                  <div className="bg-slate-50 border border-slate-200 rounded-2xl rounded-tl-md px-4 py-3">
                    <div className="flex items-center gap-3 mb-3">
                      <Brain className="h-4 w-4 text-slate-600" />
                      <p className="text-slate-900 font-medium">AI Assistant</p>
                    </div>
                    <div className="flex items-center justify-center py-6">
                      <div className="relative">
                        <div className="animate-spin rounded-full h-8 w-8 border-4 border-slate-200"></div>
                        <div className="animate-spin rounded-full h-8 w-8 border-4 border-primary-600 border-t-transparent absolute top-0"></div>
                      </div>
                      <span className="ml-3 text-slate-600">Analyzing your question...</span>
                    </div>
                  </div>
                </div>
              </div>
            ) : queryResult && queryResult.status === 'success' ? (
              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-slate-100 rounded-full flex items-center justify-center">
                    <Bot className="h-5 w-5 text-slate-700" />
                  </div>
                </div>
                <div className="flex-1">
                  <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-md px-4 py-3 shadow-sm">
                    <div className="flex items-center gap-3 mb-4">
                      <Brain className="h-4 w-4 text-slate-600" />
                      <p className="text-slate-900 font-medium">AI Assistant</p>
                    </div>

                    {/* Answer Content */}
                    <div className="text-slate-900 leading-relaxed mb-4 space-y-1">
                      {formatAnswer(queryResult.answer)}
                    </div>

                    {/* Sources */}
                    {queryResult.sources && queryResult.sources.length > 0 && (
                      <div className="border-t border-slate-200 pt-4">
                        <h4 className="text-sm font-semibold text-slate-900 mb-3 flex items-center gap-2">
                          <FileText className="h-4 w-4" />
                          References ({queryResult.sources.length})
                        </h4>
                        <div className="space-y-2 max-h-60 overflow-y-auto">
                          {queryResult.sources.map((source, index) => (
                            <SourceCard key={source.id} source={source} index={index + 1} />
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Metadata */}
                    {queryResult.metadata && (
                      <div className="border-t border-slate-200 pt-4 mt-4">
                        <div className="flex flex-wrap items-center gap-3 text-xs">
                          <div className="flex items-center gap-2 bg-slate-50 px-3 py-2 rounded-full border border-slate-200">
                            <Clock className="h-3 w-3 text-slate-600" />
                            <span className="text-slate-700 font-medium">
                              {queryResult.metadata.generation_metadata.latency_seconds.toFixed(2)}s
                            </span>
                          </div>
                          <div className="flex items-center gap-2 bg-emerald-50 px-3 py-2 rounded-full border border-emerald-200">
                            <Database className="h-3 w-3 text-emerald-600" />
                            <span className="text-emerald-700 font-medium">
                              {queryResult.metadata.documents_retrieved} sources
                            </span>
                          </div>
                          {queryResult.metadata.generation_metadata.tokens_used && (
                            <div className="flex items-center gap-2 bg-purple-50 px-3 py-2 rounded-full border border-purple-200">
                              <Brain className="h-3 w-3 text-purple-600" />
                              <span className="text-purple-700 font-medium">
                                {queryResult.metadata.generation_metadata.tokens_used} tokens
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ) : queryResult && queryResult.status === 'error' ? (
              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                    <AlertCircle className="h-5 w-5 text-red-600" />
                  </div>
                </div>
                <div className="flex-1">
                  <div className="bg-red-50 border border-red-200 rounded-2xl rounded-tl-md px-4 py-3">
                    <div className="flex items-center gap-3 mb-3">
                      <AlertCircle className="h-4 w-4 text-red-600" />
                      <p className="text-red-900 font-medium">Error</p>
                    </div>
                    <p className="text-red-800">{queryResult.error}</p>
                  </div>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
};

