import React from 'react';
import { FileText, ExternalLink, Clock, Database, Brain, CheckCircle, AlertCircle } from 'lucide-react';
import { QueryResponse, Source } from '../types';

// Function to format answer text with proper styling
const formatAnswer = (text: string) => {
  if (!text) return '';

  // Split into paragraphs
  const paragraphs = text.split('\n\n');

  return paragraphs.map((paragraph, index) => {
    const trimmed = paragraph.trim();
    if (!trimmed) return null;

    // Check for bullet points
    if (trimmed.startsWith('•') || trimmed.startsWith('-') || trimmed.startsWith('*')) {
      const items = trimmed.split('\n').filter(item => item.trim());
      return (
        <ul key={index} className="list-disc list-inside space-y-2 mb-4 ml-4">
          {items.map((item, itemIndex) => (
            <li key={itemIndex} className="text-gray-700 leading-relaxed">
              {item.replace(/^[-•*]\s*/, '')}
            </li>
          ))}
        </ul>
      );
    }

    // Check for numbered lists
    if (/^\d+\./.test(trimmed)) {
      const items = trimmed.split('\n').filter(item => item.trim());
      return (
        <ol key={index} className="list-decimal list-inside space-y-2 mb-4 ml-4">
          {items.map((item, itemIndex) => (
            <li key={itemIndex} className="text-gray-700 leading-relaxed">
              {item.replace(/^\d+\.\s*/, '')}
            </li>
          ))}
        </ol>
      );
    }

    // Check for key points or important information
    if (trimmed.includes('Key:') || trimmed.includes('Note:') || trimmed.includes('Important:')) {
      return (
        <div key={index} className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-4 rounded-r-lg">
          <div className="flex items-start">
            <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
            <div className="text-blue-800 leading-relaxed">
              {trimmed}
            </div>
          </div>
        </div>
      );
    }

    // Regular paragraphs
    return (
      <p key={index} className="text-gray-800 leading-relaxed mb-4 last:mb-0">
        {trimmed}
      </p>
    );
  });
};

interface ResultDisplayProps {
  result: QueryResponse | null;
  loading: boolean;
}

export const ResultDisplay: React.FC<ResultDisplayProps> = ({ result, loading }) => {
  if (loading) {
    return (
      <div className="card">
        <div className="flex flex-col items-center justify-center py-12">
          <div className="relative">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-slate-200"></div>
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-600 border-t-transparent absolute top-0"></div>
          </div>
          <div className="mt-6 text-center">
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Analyzing Your Question</h3>
            <p className="text-slate-600 text-sm max-w-md">
              Searching through Australian immigration law documents and generating a comprehensive response...
            </p>
            <div className="mt-4 flex items-center justify-center gap-2 text-xs text-slate-500">
              <Brain className="h-4 w-4" />
              <span>Powered by gpt-oss-20b</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="card">
        <div className="text-center py-12">
          <div className="bg-gradient-to-br from-slate-100 to-slate-200 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-6">
            <Brain className="h-10 w-10 text-slate-600" />
          </div>
          <h3 className="text-xl font-semibold text-slate-900 mb-3">Ready to Help</h3>
          <p className="text-slate-600 text-base max-w-md mx-auto leading-relaxed">
            Ask any question about Australian immigration law. I'll search through official documents
            and provide you with accurate, comprehensive answers powered by advanced AI.
          </p>
          <div className="mt-6 flex items-center justify-center gap-2 text-sm text-slate-500">
            <Database className="h-4 w-4" />
            <span>Access to 1000+ immigration law documents</span>
          </div>
        </div>
      </div>
    );
  }

  if (result.status === 'error') {
    return (
      <div className="card">
        <div className="bg-gradient-to-br from-red-50 to-red-100 border border-red-200 rounded-xl p-6">
          <div className="flex items-start gap-4">
            <div className="bg-red-100 rounded-full p-3 flex-shrink-0">
              <AlertCircle className="h-6 w-6 text-red-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-red-900 mb-2">Unable to Process Request</h3>
              <p className="text-red-800 leading-relaxed">{result.error}</p>
              <div className="mt-4">
                <button
                  onClick={() => window.location.reload()}
                  className="inline-flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Answer Section */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Brain className="h-5 w-5 text-primary-600" />
          <h2 className="text-xl font-semibold text-gray-900">Answer</h2>
        </div>
        
        <div className="prose prose-gray max-w-none">
          <div className="bg-gradient-to-br from-slate-50 to-white border border-slate-200 rounded-lg p-6 shadow-sm">
            <div className="text-gray-800 leading-relaxed whitespace-pre-wrap text-base">
              {formatAnswer(result.answer)}
            </div>
          </div>
        </div>

        {result.metadata && (
          <div className="mt-6 pt-4 border-t border-slate-200">
            <div className="flex flex-wrap items-center gap-4 text-sm">
              <div className="flex items-center gap-2 bg-slate-50 px-3 py-2 rounded-full border border-slate-200">
                <Clock className="h-4 w-4 text-slate-600" />
                <span className="text-slate-700 font-medium">
                  {result.metadata.generation_metadata.latency_seconds.toFixed(2)}s response time
                </span>
              </div>
              <div className="flex items-center gap-2 bg-emerald-50 px-3 py-2 rounded-full border border-emerald-200">
                <Database className="h-4 w-4 text-emerald-600" />
                <span className="text-emerald-700 font-medium">
                  {result.metadata.documents_retrieved} sources analyzed
                </span>
              </div>
              {result.metadata.generation_metadata.tokens_used && (
                <div className="flex items-center gap-2 bg-purple-50 px-3 py-2 rounded-full border border-purple-200">
                  <Brain className="h-4 w-4 text-purple-600" />
                  <span className="text-purple-700 font-medium">
                    {result.metadata.generation_metadata.tokens_used} tokens processed
                  </span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Sources Section */}
      {result.sources && result.sources.length > 0 && (
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <FileText className="h-5 w-5 text-primary-600" />
            <h2 className="text-xl font-semibold text-gray-900">Sources</h2>
            <span className="text-sm text-gray-500">({result.sources.length} documents)</span>
          </div>

          <div className="space-y-4">
            {result.sources.map((source, index) => (
              <SourceCard key={source.id} source={source} index={index + 1} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const SourceCard: React.FC<{ source: Source; index: number }> = ({ source, index }) => {
  const similarityPercentage = Math.round(source.similarity * 100);

  return (
    <div className="bg-gradient-to-r from-white to-slate-50 border border-slate-200 rounded-xl p-5 hover:shadow-md hover:border-slate-300 transition-all duration-200">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-2">
            <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
              <span className="text-sm font-bold text-primary-700">#{index}</span>
            </div>
            <h3 className="font-semibold text-slate-900 text-lg leading-tight truncate">
              {source.title}
            </h3>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-600 mb-3">
            <FileText className="h-4 w-4 text-slate-500" />
            <span className="font-medium">{source.source}</span>
            {source.section && source.section !== 'Unknown' && (
              <>
                <span className="text-slate-400">•</span>
                <span>{source.section}</span>
              </>
            )}
          </div>
        </div>
        <div className="flex-shrink-0 ml-4">
          <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold ${
            similarityPercentage >= 80
              ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
              : similarityPercentage >= 60
              ? 'bg-yellow-100 text-yellow-800 border border-yellow-200'
              : 'bg-slate-100 text-slate-700 border border-slate-200'
          }`}>
            <CheckCircle className="h-3 w-3" />
            {similarityPercentage}% relevant
          </div>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
        <p className="text-slate-700 leading-relaxed line-clamp-3 text-sm">
          {source.content_preview}
        </p>
      </div>
    </div>
  );
};

