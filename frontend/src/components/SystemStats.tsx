import React, { useState, useEffect } from 'react';
import { BarChart3, Database, Brain, Settings, RefreshCw, Cpu, HardDrive, Zap, Activity } from 'lucide-react';
import { ragApi } from '../api';
import { SystemStats as SystemStatsType } from '../types';

export const SystemStats: React.FC = () => {
  const [stats, setStats] = useState<SystemStatsType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const data: SystemStatsType = await ragApi.getSystemStats();
      setStats(data);
    } catch (err) {
      setError('Failed to load system statistics');
      console.error('Error fetching stats:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
          <span className="ml-3 text-gray-600">Loading system stats...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
          <button
            onClick={fetchStats}
            className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="card">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-primary-100 to-primary-200 rounded-lg">
            <Activity className="h-6 w-6 text-primary-700" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900">System Analytics</h2>
            <p className="text-sm text-slate-600">Real-time performance metrics</p>
          </div>
        </div>
        <button
          onClick={fetchStats}
          className="inline-flex items-center gap-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition-colors text-sm font-medium"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </button>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 gap-2">
        {/* Documents */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Database className="h-4 w-4 text-gray-600" />
              <div className="text-xs font-medium text-gray-900">Vector Database</div>
            </div>
            <div className="text-xs text-gray-600">
              {stats.vector_store.total_documents} docs
            </div>
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {stats.vector_store.collection_name}
          </div>
        </div>

        {/* Embeddings */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-gray-600" />
              <div className="text-xs font-medium text-gray-900">Embeddings</div>
            </div>
            <div className="text-xs text-gray-600">
              {stats.retrieval.embedding_dimension} dims
            </div>
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {stats.retrieval.embedding_model.split('/').pop()}
          </div>
        </div>

        {/* AI Model */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Brain className="h-4 w-4 text-gray-600" />
              <div className="text-xs font-medium text-gray-900">AI Model</div>
            </div>
            <div className="text-xs text-gray-600">
              {stats.pipeline_config.max_tokens} tokens
            </div>
          </div>
          <div className="text-xs text-gray-500 mt-1">
            gpt-oss-20b • MoE
          </div>
        </div>

        {/* Performance */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Cpu className="h-4 w-4 text-gray-600" />
              <div className="text-xs font-medium text-gray-900">Retrieval</div>
            </div>
            <div className="text-xs text-gray-600">
              Top-K: {stats.pipeline_config.top_k_results}
            </div>
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {stats.pipeline_config.chunk_size} token chunks
          </div>
        </div>
      </div>

    </div>
  );
};
